# torch profiler kernel summary — decode_short_mtp1

Capture window: 1.20s, completion_tokens=128, max_tokens=128

Trace files: 3, total kernel time aggregated: 2273.2 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 21.03 | 478.03 | 35964 | 13.29 | `_w8a8_triton_block_scaled_mm` |
| 2 | 15.40 | 350.13 | 13024 | 26.88 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 7.91 | 179.79 | 13320 | 13.50 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 4 | 5.56 | 126.28 | 3212 | 39.31 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 5 | 4.82 | 109.67 | 5986 | 18.32 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 6 | 4.37 | 99.37 | 6512 | 15.26 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 7 | 2.95 | 66.98 | 43700 | 1.53 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 8 | 2.75 | 62.52 | 6068 | 10.30 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_s161616gemm_bf16_32x32_64x1_tn_align8>(cutlass_80...` |
| 9 | 2.72 | 61.86 | 35816 | 1.73 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 10 | 2.43 | 55.35 | 6512 | 8.50 | `void vllm::act_and_mul_kernel<c10::BFloat16, __nv_bfloat162, &(c10::BFloat16 vllm::silu_kernel<c...` |
| 11 | 2.21 | 50.21 | 150 | 334.76 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 12 | 2.20 | 50.03 | 13024 | 3.84 | `mhc_pre_big_fuse_tilelang_kernel` |
| 13 | 1.83 | 41.65 | 42476 | 0.98 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 14 | 1.79 | 40.76 | 12540 | 3.25 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_32x32_128x2_tn_align8>(cutl...` |
| 15 | 1.77 | 40.35 | 12728 | 3.17 | `mhc_fused_tilelang_kernel` |
| 16 | 1.37 | 31.11 | 3066 | 10.15 | `_fp8_paged_mqa_logits_rowwise_kernel` |
| 17 | 1.13 | 25.58 | 6068 | 4.22 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 18 | 1.12 | 25.37 | 6512 | 3.90 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 19 | 1.02 | 23.09 | 6512 | 3.55 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 20 | 0.99 | 22.61 | 9176 | 2.46 | `_save_partial_states_kernel` |
| 21 | 0.96 | 21.87 | 3108 | 7.04 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_s161616gemm_bf16_16x16_128x2_tn_align8>(cutlass_8...` |
| 22 | 0.94 | 21.26 | 438 | 48.53 | `_accumulate_fp8ds_global_slots_attention_chunk_multihead_kernel` |
| 23 | 0.93 | 21.21 | 6068 | 3.49 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 24 | 0.87 | 19.87 | 11972 | 1.66 | `_dequantize_global_slots_k_kernel` |
| 25 | 0.85 | 19.29 | 12728 | 1.52 | `triton_red_fused_rms_norm_0` |
| 26 | 0.81 | 18.48 | 9176 | 2.01 | `void cublasLt::splitKreduce_kernel<32, 16, int, float, float, float, float, false, float, float,...` |
| 27 | 0.67 | 15.16 | 6512 | 2.33 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 28 | 0.53 | 12.06 | 442 | 27.28 | `void at::native::(anonymous namespace)::cunn_SoftMaxForward<4, float, float, float, at::native::...` |
| 29 | 0.50 | 11.43 | 6512 | 1.76 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 30 | 0.49 | 11.12 | 6658 | 1.67 | `void at::native::elementwise_kernel<128, 4, at::native::gpu_kernel_impl_nocast<at::native::direc...` |
