"""ChemRAG integration and baseline test runner."""

import json
import time
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional, Tuple

import requests

BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"
STREAM_ENDPOINT = f"{BASE_URL}/api/chat/stream"
DEFAULT_SESSION_ID = "integration-test-session"
CHAT_TIMEOUT_SEC = 60
STREAM_TIMEOUT_SEC = 120

# 中文回归问题集（优先贴近当前化学语料）
REGRESSION_QUESTIONS = [
    "卟啉修饰二氧化钛复合材料的主要优势是什么？",
    "文献中提到的光催化性能提升机理有哪些？",
    "请总结该材料在可见光响应方面的结论。",
    "文献里有没有提到 ZnO 与卟啉结合的作用？",
    "该研究中常见的表征手段有哪些？",
]


def _percentile(values: List[float], p: int) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = int(round((p / 100) * (len(sorted_values) - 1)))
    return sorted_values[idx]


def _now_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def test_health_check() -> bool:
    """Test if backend is running and accessible."""
    try:
        # Try to call a simple endpoint or just check if server is up
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return response.status_code < 500
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_chat_endpoint(question: str) -> Tuple[Optional[dict], float]:
    """Test synchronous chat endpoint and return latency in ms."""
    try:
        payload = {"session_id": DEFAULT_SESSION_ID, "question": question}
        print(f"\n📤 Sending chat request: {question}")
        start = time.perf_counter()
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=CHAT_TIMEOUT_SEC)
        latency_ms = (time.perf_counter() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received")
            print(f"   Latency: {latency_ms:.1f} ms")
            print(f"   Answer length: {len(data.get('answer', ''))}")
            print(f"   Sources: {len(data.get('sources', []))}")
            print(f"   Images: {len(data.get('images', []))}")
            return data, latency_ms
        else:
            print(f"❌ Chat endpoint returned {response.status_code}")
            print(f"   Response: {response.text}")
            return None, latency_ms
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return None, 0.0


def test_stream_endpoint(question: str) -> Tuple[bool, float, float]:
    """Test streaming endpoint and return (ok, first_chunk_ms, total_ms)."""
    try:
        payload = {"session_id": DEFAULT_SESSION_ID, "question": question}
        print(f"\n📤 Sending stream request: {question}")
        start = time.perf_counter()
        
        response = requests.post(
            STREAM_ENDPOINT,
            json=payload,
            stream=True,
            timeout=(10, STREAM_TIMEOUT_SEC),
        )

        first_chunk_ms = 0.0
        
        if response.status_code != 200:
            print(f"❌ Stream endpoint returned {response.status_code}")
            return False, first_chunk_ms, 0.0
        
        events_received = 0
        chunks_received = 0
        final_answer = ""
        
        for line in response.iter_lines():
            elapsed = time.perf_counter() - start
            if elapsed > STREAM_TIMEOUT_SEC:
                print(f"  ⚠️  Stream exceeded timeout ({STREAM_TIMEOUT_SEC}s)")
                return False, first_chunk_ms, elapsed * 1000
            if not line:
                continue
            
            line_str = line.decode() if isinstance(line, bytes) else line
            
            # Parse SSE format
            if line_str.startswith("data: "):
                try:
                    event_data = json.loads(line_str[6:])
                    event_type = event_data.get("type")
                    events_received += 1
                    
                    if event_type == "start":
                        print("  ➡️  Stream started")
                    elif event_type == "chunk":
                        chunks_received += 1
                        if first_chunk_ms == 0.0:
                            first_chunk_ms = (time.perf_counter() - start) * 1000
                        content = event_data.get("content", "")
                        if len(content) > 50:
                            print(f"  📝 Chunk {chunks_received}: {content[:50]}...")
                        else:
                            print(f"  📝 Chunk {chunks_received}: {content}")
                    elif event_type == "end":
                        final_answer = event_data.get("answer", "")
                        sources = event_data.get("sources", [])
                        images = event_data.get("images", [])
                        print(f"  ✅ Stream ended")
                        print(f"     Total chunks: {chunks_received}")
                        print(f"     Final answer length: {len(final_answer)}")
                        print(f"     Sources: {len(sources)}")
                        print(f"     Images: {len(images)}")
                    elif event_type == "error":
                        error = event_data.get("error", "Unknown error")
                        print(f"  ⚠️  Stream error: {error}")
                        total_ms = (time.perf_counter() - start) * 1000
                        return False, first_chunk_ms, total_ms
                except json.JSONDecodeError:
                    print(f"  ⚠️  Failed to parse JSON: {line_str}")
        
        total_ms = (time.perf_counter() - start) * 1000
        print(f"   First chunk latency: {first_chunk_ms:.1f} ms")
        print(f"   Total stream latency: {total_ms:.1f} ms")
        print(f"✅ Stream completed with {events_received} events")
        return events_received > 0, first_chunk_ms, total_ms
        
    except requests.exceptions.Timeout:
        print(f"❌ Stream endpoint timed out")
        return False, 0.0, 0.0
    except Exception as e:
        print(f"❌ Stream endpoint error: {e}")
        return False, 0.0, 0.0


def run_all_tests() -> Dict:
    """Run integration tests and emit baseline metrics."""
    print("=" * 60)
    print("🧪 ChemRAG Integration Tests")
    print("=" * 60)
    
    results: Dict = {}
    chat_latencies: List[float] = []
    stream_first_chunk_latencies: List[float] = []
    stream_total_latencies: List[float] = []
    
    # Test 1: Health check
    print("\n[1/4] Health Check")
    results["health"] = test_health_check()
    if not results["health"]:
        print("⚠️  Backend not responding. Start backend with:")
        print("   cd backend && python main.py")
        return results
    print("✅ Backend is running")
    
    # Test 2: Chat endpoint
    print("\n[2/4] Chat Endpoint")
    chat_result, chat_latency = test_chat_endpoint("卟啉是什么？")
    results["chat"] = chat_result is not None
    if chat_latency > 0:
        chat_latencies.append(chat_latency)
    
    # Test 3: Streaming endpoint
    print("\n[3/4] Streaming Endpoint")
    stream_ok, first_chunk_ms, stream_total_ms = test_stream_endpoint("卟啉的作用是什么？")
    results["stream"] = stream_ok
    if first_chunk_ms > 0:
        stream_first_chunk_latencies.append(first_chunk_ms)
    if stream_total_ms > 0:
        stream_total_latencies.append(stream_total_ms)
    
    # Test 4: Multiple questions (stress test)
    print(f"\n[4/4] Stress Test ({len(REGRESSION_QUESTIONS)} questions)")
    
    all_passed = True
    for i, q in enumerate(REGRESSION_QUESTIONS, 1):
        print(f"\n   Question {i}/{len(REGRESSION_QUESTIONS)}: {q}")
        result, latency = test_chat_endpoint(q)
        if not result:
            all_passed = False
        if latency > 0:
            chat_latencies.append(latency)
    
    results["stress"] = all_passed
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"  • Health: {'✅' if results['health'] else '❌'}")
    print(f"  • Chat: {'✅' if results['chat'] else '❌'}")
    print(f"  • Stream: {'✅' if results['stream'] else '❌'}")
    print(f"  • Stress: {'✅' if results['stress'] else '❌'}")

    # 基线速度统计
    perf = {
        "chat_ms": {
            "count": len(chat_latencies),
            "p50": round(median(chat_latencies), 2) if chat_latencies else 0.0,
            "p95": round(_percentile(chat_latencies, 95), 2) if chat_latencies else 0.0,
            "p99": round(_percentile(chat_latencies, 99), 2) if chat_latencies else 0.0,
        },
        "stream_first_chunk_ms": {
            "count": len(stream_first_chunk_latencies),
            "p50": round(median(stream_first_chunk_latencies), 2) if stream_first_chunk_latencies else 0.0,
            "p95": round(_percentile(stream_first_chunk_latencies, 95), 2) if stream_first_chunk_latencies else 0.0,
            "p99": round(_percentile(stream_first_chunk_latencies, 99), 2) if stream_first_chunk_latencies else 0.0,
        },
        "stream_total_ms": {
            "count": len(stream_total_latencies),
            "p50": round(median(stream_total_latencies), 2) if stream_total_latencies else 0.0,
            "p95": round(_percentile(stream_total_latencies, 95), 2) if stream_total_latencies else 0.0,
            "p99": round(_percentile(stream_total_latencies, 99), 2) if stream_total_latencies else 0.0,
        },
    }
    results["performance"] = perf

    print("\n⏱️  Latency Baseline")
    print(f"  • Chat p50/p95/p99: {perf['chat_ms']['p50']} / {perf['chat_ms']['p95']} / {perf['chat_ms']['p99']} ms")
    print(
        f"  • Stream first-chunk p50/p95/p99: "
        f"{perf['stream_first_chunk_ms']['p50']} / {perf['stream_first_chunk_ms']['p95']} / {perf['stream_first_chunk_ms']['p99']} ms"
    )
    print(
        f"  • Stream total p50/p95/p99: "
        f"{perf['stream_total_ms']['p50']} / {perf['stream_total_ms']['p95']} / {perf['stream_total_ms']['p99']} ms"
    )

    # 落盘，满足 TEST_PLAN 可复跑要求
    output_dir = Path(__file__).resolve().parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"integration_result_{_now_str()}.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n🧾 Result artifact: {output_path}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Check if we should wait for backend to start
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if test_health_check():
                print("✅ Backend is ready!\n")
                time.sleep(1)
                break
            time.sleep(1)
    
    run_all_tests()
