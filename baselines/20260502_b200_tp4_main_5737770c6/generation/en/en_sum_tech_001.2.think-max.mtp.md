# Generation Transcript

- Case: `en_sum_tech_001`
- Language group: `en`
- Workload: `reading_summary`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 2.163885
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 718, "total_tokens": 1234, "completion_tokens": 516, "prompt_tokens_details": null}`
- Prompt tokens: 718
- Completion tokens: 516
- Total tokens: 1234

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
### Concise 100-Word Overview
The water cycle describes water’s constant motion across Earth, stored in the atmosphere, on land, and underground. Oceans hold 96% of all water (saline), while freshwater exists in lakes, reservoirs, rivers, wetlands, ice sheets, glaciers, and snowpack. Water changes form between liquid, solid, and gas. Natural drivers are solar energy (causing evaporation and evapotranspiration) and gravity (causing precipitation, runoff, and groundwater flow). Human water use, land use, and climate change impact the cycle. Understanding these impacts helps sustainable water use. Water moves naturally and through human actions, affecting availability based on pool sizes, movement rates, and water quality.

### Concept Map (Text Form)
```
Atmosphere (water vapor)
    ↑ evapotranspiration / evaporation (solar energy) ↓ precipitation (gravity)
Land Surface (lakes, rivers, reservoirs, wetlands, snowpack)
    ↓ runoff / snowmelt ↓ infiltration
Groundwater (aquifers)
    ↓ natural discharge (to rivers, ocean, springs) → Oceans (96% of all water)
```

### Key Terms (with One-Sentence Definitions)
1. **Water cycle**: The continuous movement of water among Earth’s atmosphere, land surface, and underground stores.
2. **Evaporation**: The process by which liquid water turns into water vapor using energy from the sun.
3. **Evapotranspiration**: The main way water moves into the atmosphere from land surfaces and oceans, combining evaporation and plant transpiration.
4. **Precipitation**: Rain, snow, or hail that falls from clouds due to gravity.
5. **Runoff**: Water that moves across the land surface after snowmelt or rainfall.
6. **Infiltration**: The movement of water from the surface into the ground.
7. **Groundwater recharge**: The process by which infiltrated water replenishes underground aquifers.
8. **Aquifers**: Underground layers where groundwater flows and is stored.

### Human Influence
Human actions affect water movement, storage, and availability through **water use** (e.g., withdrawing water for drinking, irrigation, or industry), **land use** (e.g., paving surfaces that reduce infiltration, or altering watersheds), and **climate change** (which alters evaporation rates, precipitation patterns, and snowpack storage). These impacts change how much water is in each pool, how fast water moves through the cycle, and water cleanliness. Sustainable water use requires understanding and managing these human influences.
````
