import sys
import time

from backend.database.session import SessionLocal
from backend.services.vision_service import analyze_civic_image


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m backend.test_vision <image_path>")
        return

    image_path = sys.argv[1]

    db = SessionLocal()

    try:
        start = time.perf_counter()

        result = analyze_civic_image(image_path, db)

        print("\nGAARD Vision AI Result")
        print("----------------------")

        for key, value in result.items():
            print(f"{key}: {value}")

        print(
            f"\nResponse time: "
            f"{time.perf_counter() - start:.2f} seconds"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()