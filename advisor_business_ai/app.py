import argparse
import json
from pathlib import Path
from graphs.business_advisor import BusinessAdvisorGraph
from utils.config import config
from utils.logging import logger


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="StartSmart AI Business Advisor")
    parser.add_argument('--idea', type=str, help='The business idea to evaluate')
    parser.add_argument('--context', type=str, help='Path to JSON file with business context')
    parser.add_argument('--output', type=str, default='output', help='Output directory')

    args = parser.parse_args()

    # Update config based on arguments
    if args.output:
        config.OUTPUT_DIR = args.output

    # Load business context if provided
    business_context = {}
    if args.context:
        try:
            with open(args.context, 'r') as f:
                business_context = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load context file: {e}")
            return

    # Get business idea
    if not args.idea:
        business_idea = input("Please describe your business idea: ")
    else:
        business_idea = args.idea

    # Initialize and run the business advisor
    advisor = BusinessAdvisorGraph()
    result = advisor.run(business_idea, business_context)

    # Output results
    if result.get("status") == "success":
        print("\n🎉 Business Plan Created Successfully!")
        print(f"Plan saved to: {result['business_plan']['file_path']}")

        print("\n📝 Review Summary:")
        print(result["review"]["feedback"])

        print("\n⭐ Plan Rating:", result["review"]["rating"], "/ 10")
    else:
        print("❌ Failed to create business plan:")
        print(result.get("error", "Unknown error"))


if __name__ == "__main__":
    main()