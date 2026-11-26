import sys
from backend.services.image_quality_service import check_image_quality


if len(sys.argv) != 2:
    print("Usage: python -m backend.test_image_quality <image_path>")
    sys.exit(1)

image_path = sys.argv[1]

result = check_image_quality(image_path)

print("\nGAARD Image Quality Report")
print("--------------------------")

for key, value in result.items():
    print(f"{key}: {value}")