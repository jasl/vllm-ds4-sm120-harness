# Generation Transcript

- Case: `en_sum_tech_001`
- Language group: `en`
- Workload: `reading_summary`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 2.194681
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 718, "total_tokens": 1251, "completion_tokens": 533, "prompt_tokens_details": null}`
- Prompt tokens: 718
- Completion tokens: 533
- Total tokens: 1251

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
### Structured English Summary

**1. Concise 100-word overview**
The water cycle describes the continuous movement of water on Earth among storage pools—atmosphere, land surface, and underground. Water changes between liquid, solid, and gas forms. Oceans hold 96% of Earth’s water; the rest is fresh water in lakes, reservoirs, rivers, wetlands, ice sheets, glaciers, and snowpack. Solar energy and gravity drive movement: evaporation and evapotranspiration move water to the atmosphere; precipitation returns it; runoff, infiltration, and groundwater flow move it across and below the surface. Human water use, land use, and climate change affect water movement, storage, and availability. Understanding these impacts supports sustainable water use.

**2. Concept map (text form)**
```
Atmosphere ←— Evaporation / Evapotranspiration —← Oceans, Land surface
     ↓ Precipitation (rain, snow, hail)
     ↓
Land surface (lakes, rivers, wetlands, snowpack, glaciers)
     ↓ Runoff / Snowmelt
     ↓
Groundwater (aquifers) ←— Infiltration / Recharge
     ↓ Natural discharge (springs, rivers, ocean)
     ↓
Oceans (and saline lakes)
     ↑
Groundwater returns to surface → rivers, ocean, springs
```

**3. Key terms (8+)**
- **Water cycle**: The continuous movement and storage of water on Earth.
- **Evaporation**: Process by which solar energy turns liquid water into water vapor.
- **Evapotranspiration**: The main way water moves from land and oceans into the atmosphere.
- **Precipitation**: Rain, snow, or hail falling from clouds due to gravity.
- **Runoff**: Water moving across the land surface toward streams, rivers, or oceans.
- **Infiltration**: The movement of water from the surface into the ground.
- **Groundwater**: Water stored underground within aquifers.
- **Groundwater recharge**: The process by which water enters an aquifer from the surface.
- **Watershed**: A large-scale area over which water moves across the landscape.

**4. Human influence**
Human actions affect water movement, storage, and availability through water use (e.g., withdrawing water from rivers, lakes, or groundwater), land use changes (e.g., paving surfaces that reduce infiltration), and climate change (which can alter precipitation patterns and evaporation rates). These impacts modify how much water is stored in each pool, the speed and timing of water movement through the cycle, and the cleanliness of available water. Understanding these effects helps guide efforts to use water sustainably.
````
