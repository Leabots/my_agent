from .agent import Agent
import json


def test(base_url, model, api_key, message="This is a test message from Zhuhai No. 1 High School!"):
    """Quick test for core Agent functionality.
    
    Args:
        base_url: Base URL for API requests
        model: Model to use for completions
        api_key: API key for authentication
        message: Test message to send
    
    Returns:
        Dictionary with test results from all methods
    """
    print("=" * 60)
    print("Starting Agent Quick Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Message: {message}\n")
    
    results = {}

    # Set default configuration
    Agent.set_default(base_url, model, api_key)
    print("✓ Default configuration set\n")

    # Create agent instance
    agent = Agent()
    print(f"✓ Agent created: {agent}\n")
    
    # Test 1: Normal complete
    print("-" * 60)
    print("Test 1: Normal complete()")
    print("-" * 60)
    try:
        result = agent.complete(message)
        print(f"✓ Complete succeeded!")
        print(f"Content: {result['content']}")
        print(f"Tokens: {result['total_tokens']} total")
        results['complete'] = result
    except Exception as e:
        print(f"✗ Complete failed: {e}")
        results['complete'] = {'error': str(e)}
    print()
    
    # Clear history for next test
    agent.clear_history()

    # Test 2: Streaming complete
    print("-" * 60)
    print("Test 2: stream_complete() (streaming output)")
    print("-" * 60)
    try:
        full_content = ""
        final_response = None
        print("Streaming:", end=" ", flush=True)
        for chunk in agent.stream_complete(message):
            if "done" in chunk and chunk["done"]:
                final_response = chunk["final_response"]
                break
            if "delta" in chunk and chunk["delta"]:
                print(chunk["delta"], end="", flush=True)
                full_content += chunk["delta"]
        print("\n✓ Streaming succeeded!")
        print(f"Full content length: {len(full_content)}")
        if final_response:
            print(f"Tokens: {final_response['total_tokens']} total")
        results['stream_complete'] = final_response
    except Exception as e:
        print(f"\n✗ Streaming failed: {e}")
        results['stream_complete'] = {'error': str(e)}
    print()

    # Test 3: History functionality
    print("-" * 60)
    print("Test 3: History management")
    print("-" * 60)
    try:
        history = agent.history
        print(f"✓ Current history length: {len(history.history)}")
        saved_list = agent.list_saved_histories()
        print(f"✓ Saved histories available: {saved_list}")
        agent.clear_history()
        print(f"✓ History cleared, new length: {len(agent.history.history)}")
        results['history'] = {'cleared': True, 'saved_list': saved_list}
    except Exception as e:
        print(f"✗ History management failed: {e}")
        results['history'] = {'error': str(e)}
    print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        if 'error' in result:
            print(f"{test_name}: FAILED")
        else:
            print(f"{test_name}: PASSED")
    print()
    
    return results




def json_output_test(base_url, model, api_key, message="This is a JSON output test. Respond with a JSON dictionary containing exactly one key 'response' whose value is the string 'ok'."):
    """Test specifically for JSON output functionality.
    
    Args:
        base_url: Base URL for API requests
        model: Model to use for completions
        api_key: API key for authentication
        message: Test message to send
    
    Returns:
        Dictionary with test results
    """
    print("=" * 60)
    print("Starting JSON Output Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Message: {message}\n")

    # Set default configuration
    Agent.set_default(base_url, model, api_key)
    print("✓ Default configuration set\n")

    # Create agent instance
    agent = Agent()
    print(f"✓ Agent created: {agent}\n")

    # Test: JSON output
    print("-" * 60)
    print("Test: json_output()")
    print("-" * 60)
    json_message = f"{message}\n\nPlease respond with valid JSON only."
    try:
        result = agent.json_output(json_message)
        print(f"✓ JSON output succeeded!")
        print(f"Content type: {type(result['content'])}")
        if isinstance(result['content'], dict):
            print(f"Content: {json.dumps(result['content'], indent=2, ensure_ascii=False)}")
        else:
            print(f"Content: {result['content']}")
        print(f"Tokens: {result['total_tokens']} total")
        print("\n✓ Test PASSED")
        return result
    except Exception as e:
        print(f"✗ JSON output failed: {e}")
        print("\n✓ Test FAILED")
        return {'error': str(e)}
