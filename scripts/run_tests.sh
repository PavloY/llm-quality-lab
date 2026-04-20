#!/bin/bash
set -e

LEVEL=${1:-all}
ALLURE_DIR="reports/allure-results"

mkdir -p reports

echo "=== Running tests: $LEVEL ==="

case $LEVEL in
    fast)
        pytest tests/unit/ tests/integration/ -v --tb=short --alluredir=$ALLURE_DIR
        ;;
    quality)
        pytest tests/quality/ -v --tb=short -k "quick" --alluredir=$ALLURE_DIR
        ;;
    quality-full)
        pytest tests/quality/ -v --tb=short --alluredir=$ALLURE_DIR
        ;;
    safety)
        pytest tests/safety/ -v --tb=short --alluredir=$ALLURE_DIR
        ;;
    full)
        pytest tests/unit/ tests/integration/ -v --tb=short --alluredir=$ALLURE_DIR
        pytest tests/quality/ -v --tb=short -k "quick" --alluredir=$ALLURE_DIR
        pytest tests/safety/ -v --tb=short --alluredir=$ALLURE_DIR
        ;;
    report)
        allure generate $ALLURE_DIR -o reports/allure-report --clean
        allure open reports/allure-report
        ;;
    *)
        echo "Usage: $0 {fast|quality|quality-full|safety|full|report}"
        echo ""
        echo "  fast          Unit + Integration (2s, \$0)"
        echo "  quality       Ragas quick (3min, ~\$0.02)"
        echo "  quality-full  Ragas full (15min, ~\$0.08)"
        echo "  safety        Adversarial (2min, ~\$0.06)"
        echo "  full          fast + quality + safety"
        echo "  report        Generate and open Allure HTML report"
        exit 1
        ;;
esac

echo "=== Done: $LEVEL ==="
echo "To view report: bash scripts/run_tests.sh report"
