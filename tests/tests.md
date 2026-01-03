Multiplexing ovr HTTP/2
curl --http2 https://todo-fast-api-alpha.vercel.app/db-status
{"status":"connected","database":"Neon PostgreSQL"}     

 Findings:

     Small Payloads (<10KB): Benchmarks showed that Gzip introduced a ~11% overhead due to CPU compression time exceeding the negligible network transfer savings.

     Large Payloads: Gzip remains essential for users on mobile data or slow connections when fetching large task lists (100+ items).

 Optimization Made:
 Based on these data-driven insights, I implemented GZipMiddleware with a 10KB minimum threshold. This ensures that the API remains highly responsive for typical use cases while providing bandwidth efficiency for heavy data sets.


 --------------------------on Local Host--------------------------
 python tests/benchmark_gzip.py  
 ⏱️ Starting Speed Benchmark (50 iterations per test)...
 🏃 Testing WITHOUT Gzip...
 🚀 Testing WITH Gzip...

 =============================================
 🏁 BENCHMARK RESULTS (Average of 50 runs)
 =============================================
 Without Gzip:  1357.06 ms
 With Gzip:     1390.26 ms
 ---------------------------------------------
 Result: Gzip is 2.4% SLOWER on localhost
 💡 Note: On localhost, CPU compression time can exceed network savings.
    This will reverse in favor of Gzip once deployed to the cloud!
 =============================================
                                             
 ---------------------------on Cloud Vercel Deployment---------------------------                                          
  python tests/benchmark_gzip.py
 ⏱️ Starting Speed Benchmark (50 iterations per test)...
 🏃 Testing WITHOUT Gzip...
 🚀 Testing WITH Gzip...

 =============================================
 🏁 BENCHMARK RESULTS (Average of 50 runs)
 =============================================
 Without Gzip:  423.98 ms
 With Gzip:     473.09 ms
 ---------------------------------------------
 Result: Gzip is 11.6% SLOWER on localhost
 💡 Note: On localhost, CPU compression time can exceed network savings.
    This will reverse in favor of Gzip once deployed to the cloud!
 =============================================
                                 
