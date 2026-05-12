# torch profiler kernel summary — sm120_nomtp_decode_64tok_T1B

Capture window: 1.21s, completion_tokens=98, max_tokens=128

Trace files: 3, total kernel time aggregated: 2795.0 ms

| rank | time % | total ms | instances | avg us | kernel |
|---|---|---|---|---|---|
| 1 | 18.73 | 523.43 | 46728 | 11.20 | `_w8a8_triton_block_scaled_mm` |
| 2 | 12.69 | 354.59 | 17028 | 20.82 | `void marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767...` |
| 3 | 12.48 | 348.71 | 4116 | 84.72 | `_fp8_paged_mqa_logits_kernel` |
| 4 | 5.17 | 144.61 | 17226 | 8.39 | `void vllm::cross_device_reduce_1stage<__nv_bfloat16, 2>(vllm::RankData*, vllm::RankSignals, vllm...` |
| 5 | 5.13 | 143.33 | 8036 | 17.84 | `_finish_materialized_scores_with_sink_candidate_block_kernel` |
| 6 | 4.64 | 129.80 | 8514 | 15.25 | `_deepseek_v4_sm12x_fp8_einsum_kernel` |
| 7 | 4.23 | 118.19 | 46728 | 2.53 | `void per_token_group_quant_8bit_kernel<c10::BFloat16, __nv_fp8_e4m3, false, false, float>(c10::B...` |
| 8 | 4.16 | 116.29 | 56472 | 2.06 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 9 | 4.14 | 115.60 | 12742 | 9.07 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, __nv_bfloa...` |
| 10 | 2.99 | 83.68 | 8036 | 10.41 | `std::enable_if<!(false), void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, flo...` |
| 11 | 2.33 | 65.17 | 17028 | 3.83 | `mhc_pre_big_fuse_tilelang_kernel` |
| 12 | 2.32 | 64.74 | 4116 | 15.73 | `std::enable_if<true, void>::type internal::gemvx::kernel<int, int, __nv_bfloat16, float, float, ...` |
| 13 | 2.27 | 63.51 | 55242 | 1.15 | `void at::native::vectorized_elementwise_kernel<4, at::native::BUnaryFunctor<int, int, int, at::n...` |
| 14 | 1.89 | 52.70 | 16830 | 3.13 | `mhc_fused_tilelang_kernel` |
| 15 | 1.39 | 38.94 | 8514 | 4.57 | `triton_poi_fused_clamp_mul_silu_slice_0` |
| 16 | 1.11 | 31.02 | 8514 | 3.64 | `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, i...` |
| 17 | 1.08 | 30.27 | 12276 | 2.47 | `_save_partial_states_kernel` |
| 18 | 1.04 | 28.95 | 7920 | 3.66 | `void vllm::moe::topkGatingSoftplusSqrt<8, 256, 4, 16, 32, false, int, float>(float const*, bool ...` |
| 19 | 0.97 | 27.02 | 8514 | 3.17 | `void at::native::reduce_kernel<128, 4, at::native::ReduceOp<c10::BFloat16, at::native::func_wrap...` |
| 20 | 0.94 | 26.16 | 8036 | 3.26 | `void cutlass::Kernel2<cutlass_80_wmma_tensorop_bf16_s161616gemm_bf16_16x16_128x2_tn_align8>(cutl...` |
| 21 | 0.68 | 19.13 | 8514 | 2.25 | `void vllm::deepseek_v4_fused_ops::fusedDeepseekV4QNormRopeKVRopeQuantInsertKernel<c10::BFloat16>...` |
| 22 | 0.63 | 17.49 | 8754 | 2.00 | `void at::native::unrolled_elementwise_kernel<at::native::direct_copy_kernel_cuda(at::TensorItera...` |
| 23 | 0.59 | 16.51 | 25456 | 0.65 | `void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<c10::BFloat16>, std::a...` |
| 24 | 0.57 | 15.80 | 392 | 40.30 | `_fp8ds_paged_attention_with_sink_multihead_kernel` |
| 25 | 0.54 | 15.07 | 8164 | 1.85 | `kernel_cutlass_kernel_vllmv1attentionopsdeepseek_v4_opsdequant_gather_k_cutedslDequantGatherKCac...` |
| 26 | 0.53 | 14.81 | 8118 | 1.82 | `_fused_kv_compress_norm_rope_insert_sparse_attn` |
| 27 | 0.46 | 12.84 | 8514 | 1.51 | `triton_poi_fused_clamp_copy__mul_silu_slice_0` |
| 28 | 0.44 | 12.33 | 8514 | 1.45 | `triton_red_fused_rms_norm_2` |
| 29 | 0.43 | 12.16 | 8514 | 1.43 | `triton_red_fused_moe_forward_shared_rms_norm_0` |
| 30 | 0.43 | 12.10 | 16942 | 0.71 | `memcpy32_post` |
