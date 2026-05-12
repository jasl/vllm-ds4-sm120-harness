# torch profiler kernel summary — sm120_nomtp_decode_64tok_T2A

Capture window: 1.25s, completion_tokens=112, max_tokens=128

Trace files: 3, total kernel time aggregated: 2921.4 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 20.38 | 595.37 | 53336 | 11.16 | `_w8a8_triton_block_scaled_mm` |
| 2 | 13.76 | 401.98 | 19436 | 20.68 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 5.82 | 169.99 | 4704 | 36.14 | `_fp8_paged_mqa_logits_kernel` |
| 4 | 5.61 | 163.97 | 9184 | 17.85 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 5 | 5.07 | 147.98 | 9718 | 15.23 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 6 | 4.63 | 135.40 | 53336 | 2.54 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 7 | 4.52 | 132.18 | 14562 | 9.08 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 8 | 4.48 | 130.96 | 64452 | 2.03 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 9 | 4.42 | 129.18 | 19662 | 6.57 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 10 | 3.27 | 95.57 | 9184 | 10.41 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, flo...` |
| 11 | 2.54 | 74.33 | 19436 | 3.82 | `mhc_pre_big_fuse_tilelang_kernel` |
| 12 | 2.54 | 74.08 | 4704 | 15.75 | `std::enable_if<true, void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, float, ...` |
| 13 | 2.44 | 71.40 | 63054 | 1.13 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 14 | 2.05 | 59.99 | 19210 | 3.12 | `mhc_fused_tilelang_kernel` |
| 15 | 1.63 | 47.59 | 9718 | 4.90 | `triton_poi_fused_clamp_mul_silu_slice_0` |
| 16 | 1.20 | 35.01 | 9718 | 3.60 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 17 | 1.19 | 34.71 | 14012 | 2.48 | `_save_partial_states_kernel` |
| 18 | 1.13 | 32.96 | 9040 | 3.65 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 19 | 1.07 | 31.17 | 9718 | 3.21 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 20 | 1.02 | 29.76 | 9184 | 3.24 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 21 | 0.74 | 21.76 | 9718 | 2.24 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 22 | 0.68 | 19.77 | 9986 | 1.98 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 23 | 0.67 | 19.68 | 448 | 43.92 | `_fp8ds_paged_attention_with_sink_multihead_kernel` |
| 24 | 0.66 | 19.15 | 29068 | 0.66 | `void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<c10::BFloat16>, std::a...` |
| 25 | 0.59 | 17.25 | 9312 | 1.85 | `kernel_cutlass_kernel_vllmv1attentionopsdeepseek_v4_opsdequant_gather_k_cutedslDequantGatherKCac...` |
| 26 | 0.58 | 16.93 | 9266 | 1.83 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 27 | 0.51 | 14.77 | 9718 | 1.52 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 28 | 0.48 | 13.97 | 9718 | 1.44 | `triton_red_fused_moe_forward_shared_rms_norm_0` |
| 29 | 0.47 | 13.82 | 19350 | 0.71 | `memcpy32_post` |
| 30 | 0.44 | 12.99 | 9718 | 1.34 | `triton_red_fused_rms_norm_2` |
