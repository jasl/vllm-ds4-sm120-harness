# torch profiler kernel summary — sm120_nomtp_decode_64tok_T1D

Capture window: 1.42s, completion_tokens=127, max_tokens=128

Trace files: 3, total kernel time aggregated: 3320.3 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 20.29 | 673.72 | 60416 | 11.15 | `_w8a8_triton_block_scaled_mm` |
| 2 | 13.64 | 452.99 | 22016 | 20.58 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 5.81 | 192.93 | 5334 | 36.17 | `_fp8_paged_mqa_logits_kernel` |
| 4 | 5.62 | 186.60 | 10414 | 17.92 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 5 | 5.05 | 167.63 | 11008 | 15.23 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 6 | 4.61 | 153.21 | 60416 | 2.54 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 7 | 4.51 | 149.83 | 16512 | 9.07 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 8 | 4.50 | 149.36 | 22272 | 6.71 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 9 | 4.47 | 148.49 | 73002 | 2.03 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 10 | 3.27 | 108.42 | 10414 | 10.41 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, flo...` |
| 11 | 2.54 | 84.23 | 22016 | 3.83 | `mhc_pre_big_fuse_tilelang_kernel` |
| 12 | 2.53 | 84.02 | 5334 | 15.75 | `std::enable_if<true, void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, float, ...` |
| 13 | 2.44 | 80.92 | 71424 | 1.13 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 14 | 2.04 | 67.89 | 21760 | 3.12 | `mhc_fused_tilelang_kernel` |
| 15 | 1.63 | 54.10 | 11008 | 4.91 | `triton_poi_fused_clamp_mul_silu_slice_0` |
| 16 | 1.19 | 39.60 | 11008 | 3.60 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 17 | 1.19 | 39.38 | 15872 | 2.48 | `_save_partial_states_kernel` |
| 18 | 1.12 | 37.33 | 10240 | 3.65 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 19 | 1.07 | 35.39 | 11008 | 3.22 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 20 | 1.01 | 33.43 | 10414 | 3.21 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 21 | 0.84 | 27.82 | 10496 | 2.65 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 22 | 0.74 | 24.71 | 11008 | 2.24 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 23 | 0.73 | 24.37 | 508 | 47.98 | `_fp8ds_paged_attention_with_sink_multihead_kernel` |
| 24 | 0.67 | 22.40 | 11306 | 1.98 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 25 | 0.65 | 21.69 | 32938 | 0.66 | `void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<c10::BFloat16>, std::a...` |
| 26 | 0.59 | 19.55 | 10542 | 1.85 | `kernel_cutlass_kernel_vllmv1attentionopsdeepseek_v4_opsdequant_gather_k_cutedslDequantGatherKCac...` |
| 27 | 0.50 | 16.73 | 11008 | 1.52 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 28 | 0.48 | 15.83 | 11008 | 1.44 | `triton_red_fused_moe_forward_shared_rms_norm_0` |
| 29 | 0.47 | 15.68 | 21930 | 0.71 | `memcpy32_post` |
| 30 | 0.44 | 14.74 | 11008 | 1.34 | `triton_red_fused_rms_norm_2` |
