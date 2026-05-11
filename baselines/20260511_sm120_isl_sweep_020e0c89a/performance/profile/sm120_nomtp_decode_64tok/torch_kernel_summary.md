# torch profiler kernel summary — sm120_nomtp_decode_64tok

Capture window: 0.87s, completion_tokens=64, max_tokens=64

Trace files: 3, total kernel time aggregated: 1872.0 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 23.33 | 436.68 | 30208 | 14.46 | `_w8a8_triton_block_scaled_mm` |
| 2 | 12.89 | 241.23 | 11008 | 21.91 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 11.91 | 222.98 | 2646 | 84.27 | `_fp8_paged_mqa_logits_kernel` |
| 4 | 5.89 | 110.27 | 11136 | 9.90 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 5 | 4.93 | 92.34 | 5166 | 17.87 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 6 | 4.48 | 83.82 | 5504 | 15.23 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 7 | 3.99 | 74.62 | 8192 | 9.11 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 8 | 2.93 | 54.94 | 36522 | 1.50 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 9 | 2.88 | 54.00 | 5166 | 10.45 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, flo...` |
| 10 | 2.60 | 48.72 | 30208 | 1.61 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 11 | 2.25 | 42.12 | 11008 | 3.83 | `mhc_pre_big_fuse_tilelang_kernel` |
| 12 | 2.23 | 41.81 | 2646 | 15.80 | `std::enable_if<true, void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, float, ...` |
| 13 | 1.84 | 34.36 | 10880 | 3.16 | `mhc_fused_tilelang_kernel` |
| 14 | 1.81 | 33.93 | 35712 | 0.95 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 15 | 1.24 | 23.16 | 5504 | 4.21 | `triton_poi_fused_clamp_mul_silu_slice_0` |
| 16 | 1.00 | 18.72 | 7936 | 2.36 | `_save_partial_states_kernel` |
| 17 | 1.00 | 18.65 | 5120 | 3.64 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 18 | 0.96 | 18.04 | 5504 | 3.28 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 19 | 0.90 | 16.89 | 5166 | 3.27 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 20 | 0.83 | 15.57 | 5504 | 2.83 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 21 | 0.66 | 12.38 | 5504 | 2.25 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 22 | 0.61 | 11.36 | 5674 | 2.00 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 23 | 0.57 | 10.64 | 16426 | 0.65 | `void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<c10::BFloat16>, std::a...` |
| 24 | 0.52 | 9.69 | 5294 | 1.83 | `kernel_cutlass_kernel_vllmv1attentionopsdeepseek_v4_opsdequant_gather_k_cutedslDequantGatherKCac...` |
| 25 | 0.49 | 9.22 | 5248 | 1.76 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 26 | 0.46 | 8.63 | 5504 | 1.57 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 27 | 0.43 | 7.96 | 5504 | 1.45 | `triton_red_fused_rms_norm_2` |
| 28 | 0.42 | 7.87 | 5504 | 1.43 | `triton_red_fused_moe_forward_shared_rms_norm_0` |
| 29 | 0.42 | 7.79 | 10922 | 0.71 | `memcpy32_post` |
| 30 | 0.40 | 7.57 | 252 | 30.04 | `_fp8ds_paged_attention_with_sink_multihead_kernel` |
