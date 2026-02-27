import traceback
import sys

def test_rag():
    try:
        from backend.app.rag.chain import invoke_rag
        print("Testing invoke_rag...")
        ans, src = invoke_rag("bonjour")
        print("Success:", ans[:50])
    except Exception as e:
        print("Error in invoke_rag:")
        traceback.print_exc()

def test_generate():
    try:
        from backend.app.services.generator import generate_document
        print("Testing generate_document...")
        ans = generate_document("attestation")
        print("Success:", ans[:50])
    except Exception as e:
        print("Error in generate_document:")
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
    test_generate()
