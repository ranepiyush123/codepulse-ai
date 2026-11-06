"""Command-line entrypoint."""
import argparse
import json
from .analyzer import analyze_repository, AnalysisError

def main():
    parser = argparse.ArgumentParser(description="Analyze change risk in a local Git repository")
    parser.add_argument("path", help="Local Git repository path")
    parser.add_argument("--limit", type=int, default=100, help="Number of recent commits (1-1000)")
    parser.add_argument("--top", type=int, default=15, help="Number of files to display")
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()
    try:
        report = analyze_repository(args.path, args.limit)
    except AnalysisError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2))
        return
    print(f"Analyzed {report['commits_analyzed']} commits, {report['files_analyzed']} files")
    print("Score  Level   File")
    for item in report["files"][:max(args.top, 0)]:
        print(f"{item['risk_score']:>5}  {item['risk_level']:<6}  {item['path']}")
    print("NOTE: heuristic scores, not verified defect probabilities")

if __name__ == "__main__":
    main()
