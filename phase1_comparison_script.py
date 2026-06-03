# COMPARISON: PANDASAI vs DIRECT SQL
# Run this after you have results from both Phase 1 (PandasAI) and Direct SQL validation

import pandas as pd
import json
from datetime import datetime

print('\n' + '='*80)
print('PANDASAI vs DIRECT SQL - RESULTS COMPARISON')
print('='*80)

# You'll need to have both result sets available
# results_phase1 = [from Phase 1 PandasAI execution]
# results_direct_sql = [from Direct SQL validation]

comparison_results = []

print("\n📊 Query-by-Query Comparison:\n")

for i, (pandasai_result, sql_result) in enumerate(zip(results_phase1, results_direct_sql), 1):
    
    print(f"\n{'─'*80}")
    print(f"Query {i}: {pandasai_result['category'].upper()}")
    print(f"{'─'*80}")
    
    query = pandasai_result['query']
    print(f"Question: {query}")
    
    # Compare success/failure
    pandasai_success = pandasai_result.get('success', False)
    sql_success = sql_result.get('success', False)
    
    print(f"\n✓ Execution Status:")
    print(f"  PandasAI: {'✅ Success' if pandasai_success else '❌ Failed'}")
    print(f"  Direct SQL: {'✅ Success' if sql_success else '❌ Failed'}")
    
    # Compare response times
    pandasai_time = pandasai_result.get('response_time', 0)
    sql_time = sql_result.get('response_time', 0)
    
    print(f"\n⏱️  Response Times:")
    print(f"  PandasAI: {pandasai_time:.3f}s")
    print(f"  Direct SQL: {sql_time:.3f}s")
    
    if pandasai_success and sql_success:
        time_diff = pandasai_time - sql_time
        time_ratio = pandasai_time / sql_time if sql_time > 0 else 0
        print(f"  Difference: {time_diff:+.3f}s ({time_ratio:.1f}x slower/faster)")
    
    # Compare results
    if pandasai_success and sql_success:
        pandasai_result_str = str(pandasai_result.get('result', 'N/A'))[:150]
        sql_result_df = sql_result.get('result_df')
        
        print(f"\n📋 Results:")
        print(f"  PandasAI: {pandasai_result_str}")
        
        if sql_result_df is not None:
            print(f"  Direct SQL:")
            print(f"    {sql_result_df.to_string(index=False)}")
        
        # Try to determine if results match
        print(f"\n✓ Result Match Status:")
        # This is a simple check - you may need to adjust based on your actual results
        try:
            # For simple numeric results
            if isinstance(pandasai_result.get('result'), (int, float)):
                pandasai_val = float(str(pandasai_result.get('result')))
                # Extract value from SQL result
                sql_val = float(sql_result_df.iloc[0, 0]) if len(sql_result_df) > 0 else None
                
                if sql_val is not None:
                    match_pct = abs((pandasai_val - sql_val) / sql_val * 100) if sql_val != 0 else 0
                    if match_pct < 1:  # Within 1%
                        print(f"  ✅ MATCH (difference < 1%)")
                    elif match_pct < 10:
                        print(f"  ⚠️  CLOSE (difference {match_pct:.1f}%)")
                    else:
                        print(f"  ❌ MISMATCH (difference {match_pct:.1f}%)")
                        print(f"    PandasAI: {pandasai_val}")
                        print(f"    SQL: {sql_val}")
                else:
                    print(f"  ⚠️  Could not parse SQL result for comparison")
            else:
                print(f"  ℹ️  Complex result type - manual review recommended")
        except Exception as e:
            print(f"  ⚠️  Could not compare: {str(e)[:100]}")
    
    elif pandasai_success and not sql_success:
        print(f"\n⚠️  Status Mismatch: PandasAI succeeded but Direct SQL failed")
        print(f"  SQL Error: {sql_result.get('error', 'Unknown')[:100]}")
    
    elif not pandasai_success and sql_success:
        print(f"\n⚠️  Status Mismatch: Direct SQL succeeded but PandasAI failed")
        print(f"  PandasAI Error: {pandasai_result.get('error', 'Unknown')[:100]}")
    
    else:
        print(f"\n❌ Both approaches failed")
        print(f"  PandasAI Error: {pandasai_result.get('error', 'Unknown')[:100]}")
        print(f"  SQL Error: {sql_result.get('error', 'Unknown')[:100]}")
    
    # Store comparison result
    comparison_results.append({
        'query_num': i,
        'category': pandasai_result['category'],
        'pandasai_success': pandasai_success,
        'sql_success': sql_success,
        'pandasai_time': pandasai_time,
        'sql_time': sql_time,
        'results_match': pandasai_success and sql_success  # You'll validate this manually
    })

# Overall summary
print(f"\n{'='*80}")
print("OVERALL COMPARISON SUMMARY")
print(f"{'='*80}")

both_success = sum(1 for r in comparison_results if r['pandasai_success'] and r['sql_success'])
pandasai_only = sum(1 for r in comparison_results if r['pandasai_success'] and not r['sql_success'])
sql_only = sum(1 for r in comparison_results if not r['pandasai_success'] and r['sql_success'])
both_failed = sum(1 for r in comparison_results if not r['pandasai_success'] and not r['sql_success'])

total = len(comparison_results)

print(f"\n✓ Execution Results:")
print(f"  Both succeeded: {both_success}/{total}")
print(f"  PandasAI only: {pandasai_only}/{total}")
print(f"  SQL only: {sql_only}/{total}")
print(f"  Both failed: {both_failed}/{total}")

if both_success > 0:
    pandasai_times = [r['pandasai_time'] for r in comparison_results if r['pandasai_success']]
    sql_times = [r['sql_time'] for r in comparison_results if r['sql_success']]
    
    avg_pandasai = sum(pandasai_times) / len(pandasai_times)
    avg_sql = sum(sql_times) / len(sql_times)
    
    print(f"\n⏱️  Performance:")
    print(f"  PandasAI average: {avg_pandasai:.3f}s")
    print(f"  Direct SQL average: {avg_sql:.3f}s")
    print(f"  Ratio: PandasAI is {avg_pandasai/avg_sql:.1f}x slower")

print(f"\n{'='*80}")

# Export comparison to CSV for further analysis
import csv

with open('phase1_comparison_results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'query_num', 'category', 'pandasai_success', 'sql_success',
        'pandasai_time_s', 'sql_time_s', 'results_match'
    ])
    writer.writeheader()
    for result in comparison_results:
        writer.writerow({
            'query_num': result['query_num'],
            'category': result['category'],
            'pandasai_success': result['pandasai_success'],
            'sql_success': result['sql_success'],
            'pandasai_time_s': f"{result['pandasai_time']:.3f}",
            'sql_time_s': f"{result['sql_time']:.3f}",
            'results_match': result['results_match']
        })

print("\n✅ Comparison results exported to: phase1_comparison_results.csv")
print("   Open this file to analyze all results in a spreadsheet")
