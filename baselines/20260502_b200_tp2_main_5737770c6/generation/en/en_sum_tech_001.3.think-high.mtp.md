# Generation Transcript

- Case: `en_sum_tech_001`
- Language group: `en`
- Workload: `reading_summary`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 2.032965
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 718, "total_tokens": 1224, "completion_tokens": 506, "prompt_tokens_details": null}`
- Prompt tokens: 718
- Completion tokens: 506
- Total tokens: 1224

## Prompt

```markdown
Read the public-domain science explainer below and produce a structured English summary.

Output requirements:
1. A concise 100-word overview.
2. A concept map in text form using arrows, showing how water moves among major pools.
3. A list of at least eight key terms with one-sentence definitions based only on the passage.
4. A section titled “Human influence” summarizing how human actions affect water movement, storage, or availability.
5. Do not introduce outside climate, policy, or regional examples.

素材来源：U.S. Geological Survey Water Science School: Water cycle
来源链接：https://www.usgs.gov/water-science-school/water-cycle
版权/授权说明：USGS-authored information is considered U.S. public domain.

【待处理素材】
The water cycle describes where water is on Earth and how it moves. Human water use, land use, and climate change all impact the water cycle. By understanding these impacts, we can work toward using water sustainably.

Viewed from space, the most striking feature of our planet is the water. In both liquid and frozen form, it covers 75% of the Earth's surface. It fills the sky with clouds. Water is practically everywhere on Earth, from inside the planet's rocky crust to inside the cells of the human body. What's important to keep in mind is that all of this water is in constant motion across our planet.

Water is stored in the atmosphere, on the land surface, and below the ground. It can be a liquid, a solid, or a gas. Liquid water can be fresh or saline. Water moves between the places it is stored. Water moves at large scales, through watersheds, the atmosphere, and below the Earth's surface. Water moves at very small scales too. It is in us, plants, and other organisms.

Oceans store 96% of all water on Earth. Ocean water is saline, meaning it’s salty. On land, saline water is stored in saline lakes. The rest of the water on Earth is fresh water. Fresh water is stored in liquid form in freshwater lakes, artificial reservoirs, rivers, and wetlands. Water is stored in solid, frozen form in ice sheets and glaciers, and in snowpack at high elevations or near Earth's poles.

As it moves, water can change form between liquid, solid, and gas. Circulation mixes water in the oceans and transports water vapor in the atmosphere. Water moves between the atmosphere and the surface through evaporation, evapotranspiration, and precipitation. Water moves across the surface through snowmelt, runoff, and streamflow. Water moves into the ground through infiltration and groundwater recharge. Underground, groundwater flows within aquifers. Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs.

Water moves naturally and because of human actions. Energy from the sun and the force of gravity drive the continual movement of water between pools. The sun’s energy causes liquid water to evaporate into water vapor. Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans. Gravity causes water to flow downward on land. It causes rain, snow, and hail to fall from clouds.

Humans and other organisms rely on water for life. The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding human impacts on the water cycle, we can work toward using water sustainably.
```

## Assistant

````markdown
### Concise 100-word Overview
The water cycle describes Earth’s water, which is in constant motion across the planet. Water is stored in the atmosphere, on land, and below ground as liquid, solid, or gas. Oceans hold 96% of Earth’s water; the rest is freshwater in lakes, rivers, ice, and groundwater. Water moves between pools via evaporation, evapotranspiration, precipitation, snowmelt, runoff, streamflow, infiltration, groundwater recharge, and natural discharge. Solar energy and gravity drive this movement. Human water use, land use, and climate change alter water movement, storage, and availability. Understanding these impacts helps toward sustainable water use.

### Concept Map (Water Movement Among Major Pools)
```
Atmosphere
   ↑ (evaporation, evapotranspiration) | ↓ (precipitation)
Oceans & Land Surface
   ↓ (runoff, streamflow) | → (infiltration, groundwater recharge)
Groundwater (aquifers)
   ↓ (natural discharge: rivers, ocean, springs) → back to Oceans & Land Surface
```

### Key Terms (One-Sentence Definitions)
1. **Evaporation**: The process by which solar energy turns liquid water into water vapor.
2. **Evapotranspiration**: The main way water moves into the atmosphere from land surfaces and oceans.
3. **Precipitation**: Rain, snow, or hail that falls from clouds due to gravity.
4. **Runoff**: Water that flows across the land surface toward streams or oceans.
5. **Infiltration**: The movement of water into the ground from the surface.
6. **Groundwater recharge**: The process by which infiltrated water enters and replenishes underground aquifers.
7. **Aquifer**: An underground layer where groundwater flows and is stored.
8. **Natural discharge**: Groundwater returning to the surface through rivers, the ocean, or springs.

### Human Influence
Human actions affect water movement, storage, and availability in three ways: (1) **water use** (e.g., withdrawing water for consumption or irrigation) alters natural pools and flow rates; (2) **land use** (e.g., construction, agriculture) changes infiltration, runoff, and evapotranspiration patterns; (3) **climate change** impacts evaporation rates, precipitation timing/amount, and snowmelt. These influences modify when and how fast water moves through the cycle and affect water cleanliness and overall availability.
````
