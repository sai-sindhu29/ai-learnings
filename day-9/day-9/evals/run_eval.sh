#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo "================================"
echo "INVOICE MODEL EVALUATION"
echo "================================"

echo "Dataset:"
python -c "import json; d=json.load(open('evals/data/labelled_invoices.json')); print('Total:',len(d)); print('CLEAN:',sum(x['expected_label']=='CLEAN' for x in d)); print('EXCEPTION:',sum(x['expected_label']=='EXCEPTION' for x in d))"

echo ""
echo "Evaluation dataset ready."
echo "Next: run Haiku and Sonnet against the same dataset."
