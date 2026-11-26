import sys
import time

from backend.agents.graph import gaard_graph


def main():

    if len(sys.argv) != 2:
        print("Usage: python -m backend.test_graph <image_path>")
        return

    initial_state = {
        "complaint_id": 1,
        "image_path": sys.argv[1],
        "retry_count": 0
    }

    start = time.perf_counter()

    result = gaard_graph.invoke(initial_state)

    print("\nGAARD Agent Workflow Result")
    print("---------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")

    if result.get("quality_status") == "retake_required":
        print("\nACTION: Please upload a clearer image.")

    elif result.get("quality_status") == "error":
        print("\nACTION: Image processing failed.")

    elif result.get("quality_status") == "good":
        print("\nACTION: Image passed quality check.")
        print("Gemini Vision analysis completed.")
    print(
        f"\nExecution time: "
        f"{time.perf_counter() - start:.2f} seconds"
    )
    print("\nDecision Result")
    print("----------------")

    decision = result.get("decision")

    if decision == "approved":
        print("Complaint accepted. Ready for department routing.")

    elif decision == "rejected":
        print("Not a civic issue. Complaint rejected.")

    elif decision == "human_review":
        print("Manual verification required.")

    elif result.get("quality_status") == "retake_required":
        print("Poor image. Request citizen to reupload.")

    else:
        print("Workflow stopped. Check error details.")


if __name__ == "__main__":
    main()