# torch profiler kernel summary — sm120_nomtp_decode_64tok_postT1A

Capture window: 1.34s, completion_tokens=109, max_tokens=128

Trace files: 3, total kernel time aggregated: 3082.4 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 18.82 | 579.99 | 51920 | 11.17 | `_w8a8_triton_block_scaled_mm` |
| 2 | 12.74 | 392.71 | 18920 | 20.76 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 12.61 | 388.54 | 4578 | 84.87 | `_fp8_paged_mqa_logits_kernel` |
| 4 | 5.18 | 159.82 | 8938 | 17.88 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 5 | 4.68 | 144.18 | 9460 | 15.24 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 6 | 4.51 | 139.17 | 19140 | 7.27 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 7 | 4.31 | 132.93 | 51920 | 2.56 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 8 | 4.17 | 128.50 | 14172 | 9.07 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 9 | 4.16 | 128.26 | 62742 | 2.04 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 10 | 3.02 | 93.12 | 8938 | 10.42 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, flo...` |
| 11 | 2.35 | 72.40 | 18920 | 3.83 | `mhc_pre_big_fuse_tilelang_kernel` |
| 12 | 2.34 | 72.00 | 4578 | 15.73 | `std::enable_if<true, void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, float, ...` |
| 13 | 2.26 | 69.76 | 61380 | 1.14 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 14 | 1.90 | 58.54 | 18700 | 3.13 | `mhc_fused_tilelang_kernel` |
| 15 | 1.42 | 43.88 | 9460 | 4.64 | `triton_poi_fused_clamp_mul_silu_slice_0` |
| 16 | 1.12 | 34.46 | 9460 | 3.64 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 17 | 1.09 | 33.70 | 13640 | 2.47 | `_save_partial_states_kernel` |
| 18 | 1.04 | 32.16 | 8800 | 3.65 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 19 | 0.97 | 29.93 | 9460 | 3.16 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 20 | 0.94 | 28.94 | 8938 | 3.24 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 21 | 0.69 | 21.23 | 9460 | 2.24 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 22 | 0.63 | 19.42 | 9722 | 2.00 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 23 | 0.62 | 19.01 | 436 | 43.59 | `_fp8ds_paged_attention_with_sink_multihead_kernel` |
| 24 | 0.60 | 18.36 | 28294 | 0.65 | `void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<c10::BFloat16>, std::a...` |
| 25 | 0.54 | 16.75 | 9066 | 1.85 | `kernel_cutlass_kernel_vllmv1attentionopsdeepseek_v4_opsdequant_gather_k_cutedslDequantGatherKCac...` |
| 26 | 0.53 | 16.45 | 9020 | 1.82 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 27 | 0.46 | 14.15 | 9460 | 1.50 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 28 | 0.44 | 13.51 | 9460 | 1.43 | `triton_red_fused_moe_forward_shared_rms_norm_0` |
| 29 | 0.44 | 13.44 | 18834 | 0.71 | `memcpy32_post` |
| 30 | 0.42 | 12.81 | 9460 | 1.35 | `triton_red_fused_rms_norm_2` |
