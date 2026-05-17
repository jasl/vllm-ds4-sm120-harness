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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 73.137694
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 797, "total_tokens": 7997, "completion_tokens": 7200, "prompt_tokens_details": null}`
- Prompt tokens: 797
- Completion tokens: 7200
- Total tokens: 7997

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

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   Source: Public-domain USGS science explainer on the water cycle (provided in the prompt).
    *   Output Requirements:
        1.  Concise 100-word overview.
        2.  Concept map (text form, arrows, showing water movement among major pools).
        3.  List of at least 8 key terms (one-sentence definitions from the passage).
        4.  Section titled "Human influence" (summarizing human actions on water movement, storage, availability).
        5.  Constraints: No outside climate, policy, or regional examples.

    *   *Self-Correction/Refinement:* The prompt explicitly provides the text. Everything must be derived *strictly* from the provided text. Let's extract the exact information needed.

    *   **Provided Text Analysis:**
        *   "The water cycle describes where water is on Earth and how it moves. Human water use, land use, and climate change all impact the water cycle."
        *   "Water is stored in the atmosphere, on the land surface, and below the ground... liquid, solid, gas. Fresh or saline."
        *   "Oceans store 96% of all water on Earth (saline). Freshwater is in lakes, reservoirs, rivers, wetlands, ice sheets, glaciers, snowpack."
        *   "Moves through evaporation, evapotranspiration, precipitation. Snowmelt, runoff, streamflow. Infiltration, groundwater recharge. Groundwater flows in aquifers. Returns via discharge into rivers, ocean, springs."
        *   "Energy from the sun and gravity drive the movement."
        *   "Humans and other organisms rely on water... How much water is available depends on the amount in each pool, the timing and speed of movement, and cleanliness."

    *   **Output Structure:**

        **1. Concise 100-word overview**
            *Draft:* The water cycle describes the constant movement of water across Earth. Water is stored in oceans, atmosphere, land, and underground as liquid, solid, or gas. Solar energy and gravity drive this circulation. Water moves between pools through evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Ocean water is saline, while freshwater exists in ice, lakes, rivers, and underground. The availability of water depends on storage amounts, the timing and speed of movement, and water cleanliness. Human water use, land use, and climate change impact this cycle, highlighting the need for sustainable water use.
            *Word count check:* ~110 words. Let's shorten it.
            The water cycle is the continuous movement of water on Earth. It is stored in oceans (96% of all water), atmosphere, land, and underground as liquid, solid, or gas. Solar energy and gravity drive its movement. Water moves through evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Oceans are saline, while freshwater is in ice, lakes, rivers, and aquifers. Availability depends on pool storage, movement speed, and water quality. Human water use, land use, and climate change impact the cycle, requiring sustainable management. (~90 words. Good.)

        **2. Concept map in text form using arrows**
            *Pool 1: Atmosphere*
            *Pool 2: Oceans (Saline)*
            *Pool 3: Land Surface / Ice*
            *Pool 4: Groundwater (Aquifers)*
            *Processes:*
            *   Evapotranspiration / Evaporation -> Atmosphere
            *   Precipitation -> Land / Oceans
            *   Runoff / Streamflow -> Oceans
            *   Infiltration / Recharge -> Groundwater
            *   Groundwater Discharge -> Oceans / Land Surface

            *Text Map:*
            Sun + Gravity
            ↓
            [Oceans]  ----(Evaporation)----> [Atmosphere] ----(Precipitation)----> [Land/Ice]
               ↑                                                                    ↓
               |---(Runoff/Streamflow)<----[Land/Ice]                               |
               |                                                                    ↓
               |                                                         (Infiltration/Recharge)
               |                                                                    ↓
               |                                                               [Groundwater]
               |                                                                    |
               |<-------------------(Groundwater Discharge)-------------------------|
               |
               (Precipitation also falls directly on Oceans)

            Let's refine this into a cleaner text diagram usable by the user.
            ```
            [Atmosphere] <--(Evaporation/Evapotranspiration)-- [Oceans & Land]
                 |
                 | (Precipitation)
                 v
            [Land Surface / Ice / Snow] --(Runoff/Streamflow)--> [Oceans]
                 |
                 | (Infiltration/Recharge)
                 v
            [Groundwater (Aquifers)] ----(Discharge)-----> [Oceans, Rivers, Springs]
            ```

        **3. List of at least 8 key terms with one-sentence definitions (based only on passage)**
            *Terms extracted:*
            1.  *Water Cycle / Hydrologic Cycle* (implicitly defined by the first sentence)
            2.  *Evaporation*: "The sun’s energy causes liquid water to evaporate into water vapor."
            3.  *Evapotranspiration*: "the main way water moves into the atmosphere from the land surface and oceans." (Also explicitly affected by humans? No, just defined).
            4.  *Precipitation*: "Water moves... through... precipitation. Gravity causes rain, snow, and hail to fall from clouds."
            5.  *Runoff*: "Water moves across the surface through snowmelt, runoff, and streamflow."
            6.  *Infiltration*: "Water moves into the ground through infiltration and groundwater recharge."
            7.  *Groundwater / Aquifers*: "Underground, groundwater flows within aquifers."
            8.  *Groundwater Discharge*: "Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs."
            9.  *Watersheds*: "Water moves at large scales, through watersheds..."
            10. *Saline/Fresh Water*: "Oceans store 96% of all water on Earth. Ocean water is saline... The rest... is fresh water."
            11. *Solar Energy / Gravity*: "Energy from the sun and the force of gravity drive the continual movement of water between pools."
            *Let's pick the best 8:*
            *   **Water Cycle**: The continuous movement and storage of water across Earth, including its changes between liquid, solid, and gas.
            *   **Evaporation**: The process driven by the sun's energy that changes liquid water into water vapor.
            *   **Evapotranspiration**: The primary movement of water from the land surface and oceans into the atmosphere.
            *   **Precipitation**: Rain, snow, and hail falling from clouds due to gravity.
            *   **Runoff**: The movement of water across the land surface, including snowmelt and streamflow.
            *   **Infiltration**: The process of water moving into the ground.
            *   **Groundwater Recharge**: The process by which water moves into the ground to replenish aquifers. (Or just combine with infiltration. The passage says "Water moves into the ground through infiltration and groundwater recharge"). Let's use: **Groundwater**: Water stored underground that flows within aquifers.
            *   **Groundwater Discharge**: The return of groundwater to the surface through rivers, the ocean, or springs.
            *   **Watershed**: The large-scale path through which water moves across the landscape. (From "Water moves at large scales, through watersheds")
            *   **Saline Water**: Water that is salty, primarily stored in oceans which make up 96% of Earth's water.
            *   **Fresh Water**: The remaining water on Earth not stored in oceans, found in lakes, rivers, ice, and underground.

            Let's use these:
            1. **Water cycle**: The description of where water is on Earth and how it moves continuously.
            2. **Evaporation**: The process where the sun’s energy causes liquid water to turn into water vapor.
            3. **Evapotranspiration**: The main way water moves into the atmosphere from the land surface and oceans.
            4. **Precipitation**: Rain, snow, and hail that fall from clouds due to the force of gravity.
            5. **Runoff**: The movement of water across the land surface, including snowmelt and streamflow.
            6. **Infiltration**: The process of water moving from the surface into the ground.
            7. **Groundwater**: Water stored underground that flows within aquifers.
            8. **Groundwater discharge**: The natural return of groundwater to the surface in rivers, the ocean, and from springs.
            9. **Watershed**: The large-scale path through which water moves across the land.
            10. **Saline water**: Salty water that fills the oceans, which store 96% of all water on Earth.
            *(I will choose 10, but the user asked for "at least 8". I will provide 10 or 9 to be safe and comprehensive. Let's do exactly 10).*

        **4. Human influence**
            *Passage quotes:*
            "Human water use, land use, and climate change all impact the water cycle."
            "Humans and other organisms rely on water for life. The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is. By understanding human impacts on the water cycle, we can work toward using water sustainably."
            "Water moves naturally and because of human actions."

            *Summary:*
            Human actions impact the water cycle in several ways. Changes in land use, water use, and climate affect water movement, storage, and availability. The amount of water available to organisms depends on the quantity in each pool, the timing and speed of water movement through the cycle, and the cleanliness of the water. By recognizing these human impacts, we can manage water more sustainably.

        **5. Formatting and Final Checks**
            *Concise 100-word overview*: Check length (exact wording provided in the prompt).
            *Concept map*: Text with arrows. Follow unique links. Groundwater to oceans. Oceans to atmosphere. Land to atmosphere. Atmosphere to land/oceans. Land to groundwater. Land to oceans.
            *Key terms*: Exactly from the passage.
            *Human influence*: No outside examples. Stick strictly to the wording in the text provided.

        Let's write down the structured output perfectly.

        **1. Overview**
        The water cycle describes the continuous movement of water on Earth. Water is stored in oceans, the atmosphere, on land, and underground as liquid, solid, or gas. Solar energy and gravity drive this movement. Water circulates via evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Oceans hold 96% of Earth's water as saline water; the rest is fresh water in ice, lakes, rivers, and aquifers. Water availability depends on the amount in each pool, the speed of movement, and cleanliness. Human water use, land use, and climate change alter the cycle. (Word count: 100 exactly).

        **2. Concept Map**
        ```
        [Atmosphere]
            ↑  |  (Evaporation / Evapotranspiration)
            |  |  (Precipitation)
            |  v
        [Land / Ice / Snow]  --(Runoff/Streamflow)--> [Oceans]
            |                                              ↑
            |  (Infiltration / Groundwater Recharge)       | (Groundwater Discharge)
            v                                              |
        [Groundwater / Aquifers] ---------------------------+
        ```
        Wait, groundwater discharge happens to the ocean, rivers, and springs. Let's map it better.
        Text-only concept map:
        ```text
        [Oceans] --(Evaporation)--> [Atmosphere] --(Precipitation)--> [Land / Ice]
           ↑                           |                                 |
           |                           | (Precipitation)                  | (Infiltration)
           |                           v                                 |
           |                       [Land] / [Oceans]                     v
           |                             |                          [Groundwater]
           |                             | (Runoff/Streamflow)
           +------------<----------------+
           | (Groundwater Discharge) |
           +--------------<------------[Groundwater] (Summer/Pools+Flows)
        ```
        Let's stick to a cleaner structured format:
        Major Pools: Oceans, Atmosphere, Land Surface/Ice, Groundwater

        Ocean → (Evaporation/Evapotranspiration) → Atmosphere
        Land Surface → (Evapotranspiration) → Atmosphere
        Atmosphere → (Precipitation) → Oceans, Land Surface
        Land Surface → (Runoff/Streamflow) → Oceans
        Land Surface → (Infiltration/Groundwater Recharge) → Groundwater
        Groundwater → (Groundwater Discharge) → Oceans, Land Surface (Rivers, Springs)

        **Text version:**
        ```
        [Oceans] ----(Evaporation)----> [Atmosphere] ----(Precipitation)----> [Land/Ice]
            ↑                                                                    |
            |---(Runoff/Streamflow)<---------------------------------------------|
            |                                                                    |
            |                      (Infiltration/Groundwater Recharge)            |
            |                                                                    ↓
            |                                                              [Groundwater]
            |                                                                    |
            +-------------------(Groundwater Discharge)--------------------------+
        ```

        **3. Key Terms**
        1.  **Water cycle**: The overall system describing where water is on Earth and how it continuously moves. (From text: "The water cycle describes where water is on Earth and how it moves... all of this water is in constant motion").
        2.  **Evaporation**: The process driven by solar energy that converts liquid water into water vapor. (From text: "The sun’s energy causes liquid water to evaporate into water vapor").
        3.  **Evapotranspiration**: The main way water moves into the atmosphere from the land surface and oceans. (From text: "Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans").
        4.  **Precipitation**: Rain, snow, and hail that fall from clouds due to gravity. (From text: "Gravity causes rain, snow, and hail to fall from clouds").
        5.  **Runoff**: The movement of water across the land surface, including from snowmelt and streamflow. (From text: "Water moves across the surface through snowmelt, runoff, and streamflow").
        6.  **Infiltration**: The process of water moving from the ground surface into the soil or rock. (From text: "Water moves into the ground through infiltration and groundwater recharge").
        7.  **Groundwater**: Water stored underground that flows within aquifers. (From text: "Underground, groundwater flows within aquifers").
        8.  **Groundwater discharge**: The natural return of groundwater to the surface, emptying into rivers, the ocean, or emerging from springs. (From text: "Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs").
        9.  **Saline water**: Salty water that makes up 96% of Earth's water, contained primarily in oceans. (From text: "Oceans store 96% of all water on Earth. Ocean water is saline").
        10. **Fresh water**: Water on Earth not contained in oceans, stored in lakes, rivers, wetlands, ice, and groundwater. (From text: "Fresh water is stored in liquid form in freshwater lakes, artificial reservoirs, rivers, and wetlands. Water is stored in solid, frozen form in ice sheets and glaciers...").

        Let's re-read the text carefully for exact wording.
        "Water moves between the atmosphere and the surface through evaporation, evapotranspiration, and precipitation."
        "Water moves across the surface through snowmelt, runoff, and streamflow."
        "Water moves into the ground through infiltration and groundwater recharge."
        "Underground, groundwater flows within aquifers. Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs."
        "Energy from the sun and the force of gravity drive the continual movement of water between pools."
        "Oceans store 96% of all water on Earth. Ocean water is saline, meaning it’s salty."

        Let's adjust the definitions to be purely sentences based on the passage.
        Def 1: The water cycle describes where water is on Earth and how it moves constantly.
        Def 2: Evaporation is the process where the sun’s energy causes liquid water to turn into water vapor.
        Def 3: Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans.
        Def 4: Precipitation is rain, snow, and hail that fall from clouds because of gravity.
        Def 5: Runoff is the way water moves across the surface, along with snowmelt and streamflow.
        Def 6: Infiltration is the way water moves into the ground.
        Def 7: Groundwater is water that flows underground within aquifers.
        Def 8: Groundwater discharge is how groundwater naturally returns to the surface in rivers, the ocean, and from springs.
        Def 9: The pool of saline ocean water stores 96% of all water on Earth.
        Def 10: Fresh water is stored in liquid form in rivers, reservoirs, and wetlands, and as solid ice in glaciers and snowpack.

        **4. Human Influence**
        "Human water use, land use, and climate change all impact the water cycle."
        "Water moves naturally and because of human actions."
        "The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is."
        "By understanding human impacts on the water cycle, we can work toward using water sustainably."

        *Draft for section:*
        Human water use, land use, and climate change impact the water cycle by affecting how water moves and how much is available. The amount of water in each pool, the timing and speed of movement through the cycle, and how clean the water is are all affected by human actions. Because water moves naturally and because of people, understanding these impacts is key to using water sustainably.

        Let's format the final answer exactly as structured by the prompt.
        "1. A concise 100-word overview.
        2. A concept map in text form using arrows, showing how water moves among major pools.
        3. A list of at least eight key terms with one-sentence definitions based only on the passage.
        4. A section titled “Human influence” summarizing how human actions affect water movement, storage, or availability.
        5. Do not introduce outside climate, policy, or regional examples."

        Let's refine the overview.
        The water cycle describes where water is on Earth and how it moves constantly. Water is stored in the atmosphere, on the land surface, and below the ground as liquid, solid, or gas. Solar energy and gravity drive this movement. Water moves via evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Oceans, storing 96% of all water, are saline, while the rest is fresh water in ice, lakes, rivers, and aquifers. Water availability depends on the amount in each pool, the speed of movement, and water cleanliness. Human water use, land use, and climate change impact this cycle.

        Let's count the words.
        The water cycle describes where water is on Earth and how it moves constantly. (10)
        Water is stored in the atmosphere, on the land surface, and below the ground as liquid, solid, or gas. (16)
        Solar energy and gravity drive this movement. (6)
        Water moves via evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. (10)
        Oceans, storing 96% of all water, are saline, while the rest is fresh water in ice, lakes, rivers, and aquifers. (17)
        Water availability depends on the amount in each pool, the speed of movement, and water cleanliness. (14)
        Human water use, land use, and climate change impact this cycle. (12)
        Total: 10 + 16 + 6 + 10 + 17 + 14 + 12 = 85 words. Good length.

        Let's refine the concept map.
        [Atmosphere] ── (Evaporation/Evapotranspiration) ── [Oceans & Land]
               ↑                                            |
               └──────────── (Precipitation) ───────────────┘
               |                                            ↓
               |                                        [Land Surface / Ice]
               |                                            |
               |              (Infiltration/Recharge)        | (Runoff/Streamflow)
               |                                            ↓
               |                                        [Oceans]
               |                                            |
               └───────── (Groundwater Discharge) ─────────[Groundwater]
               (Wait, groundwater discharge goes to rivers, ocean, springs. It comes from Groundwater -> Land Surface / Oceans).

        Let's make the concept map perfectly clear:

        ```
        [ATMOSPHERE] <----> (Evaporation/Evapotranspiration/Precipitation) <----> [OCEANS]
              |                                                                      |
              | (Precipitation)                                                      | (Runoff)
              v                                                                      ^
        [LAND SURFACE / ICE] ----> (Infiltration/Recharge) ----> [GROUNDWATER / AQUIFERS]
              ^                                                                      |
              |<------------- (Groundwater Discharge) -------------------------------|
        ```

        Let's add the arrows only for direction of movement.
        The text says:
        "Oceans store 96% of all water on Earth... The rest of the water on Earth is fresh water."
        "Water moves between the atmosphere and the surface through evaporation, evapotranspiration, and precipitation."
        "Water moves across the surface through snowmelt, runoff, and streamflow."
        "Water moves into the ground through infiltration and groundwater recharge."
        "Underground, groundwater flows within aquifers. Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs."
        "Energy from the sun and the force of gravity drive the continual movement of water between pools."
        "The sun’s energy causes liquid water to evaporate into water vapor."
        "Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans."
        "Gravity causes water to flow downward on land. It causes rain, snow, and hail to fall from clouds."

        Concept map text:
        ```
        Sun’s Energy → [EVAPORATION / EVAPOTRANSPIRATION]
        [ATMOSPHERE] ← (Evaporation/Evapotranspiration) ← [OCEANS & LAND]
        [ATMOSPHERE] → (Precipitation) → [LAND & OCEANS]
        [LAND SURFACE] → (Runoff/Streamflow) → [OCEANS]
        [LAND SURFACE] → (Infiltration/Groundwater Recharge) → [GROUNDWATER]
        [GROUNDWATER] → (Groundwater Discharge) → [OCEANS, RIVERS, SPRINGS]
        Gravity works everywhere.
        ```

        Let's structure the concept map as requested: "A concept map in text form using arrows, showing how water moves among major pools."

        ```text
        [Oceans] ----(Evaporation/Evapotranspiration)----> [Atmosphere]
             ↑                                                      |
             |                                                      | (Precipitation)
             |                                                      v
             +---------(Runoff/Streamflow)--------- [Land/Ice] <---+
                                                        |
                                                        | (Infiltration/Recharge)
                                                        v
                                                  [Groundwater]
                                                        |
                                                        | (Groundwater Discharge)
                                                        v
                                                [Oceans, Rivers, Springs]
        ```
        This elegantly covers the four major pools (Oceans, Atmosphere, Land/Ice, Groundwater) and the explicit text relationships.

        Let's ensure the queries for concept map "showing how water moves among major pools" are highly satisfied.
        Pools: Oceans, Atmosphere, Land Surface, Groundwater.
        Links:
        Oceans -> Atmosphere (Evaporation/Evapotranspiration)
        Land Surface -> Atmosphere (Evapotranspiration)
        Atmosphere -> Oceans (Precipitation)
        Atmosphere -> Land Surface (Precipitation)
        Land Surface -> Oceans (Runoff/Streamflow)
        Land Surface -> Groundwater (Infiltration/Groundwater Recharge)
        Groundwater -> Oceans (Discharge)
        Groundwater -> Land Surface (Discharge into Rivers/Springs)

        **Key Terms**
        Let's quote the passage perfectly.
        "The water cycle describes where water is on Earth and how it moves. Human water use, land use, and climate change all impact the water cycle."
        "Water is stored in the atmosphere, on the land surface, and below the ground."
        "Liquid water can be fresh or saline."
        "Oceans store 96% of all water on Earth. Ocean water is saline."
        "Fresh water is stored in liquid form in freshwater lakes, artificial reservoirs, rivers, and wetlands. Water is stored in solid, frozen form in ice sheets and glaciers, and in snowpack."
        "Water moves between the atmosphere and the surface through evaporation, evapotranspiration, and precipitation."
        "Water moves across the surface through snowmelt, runoff, and streamflow."
        "Water moves into the ground through infiltration and groundwater recharge."
        "Underground, groundwater flows within aquifers. Groundwater can return to the surface through natural discharge into rivers, the ocean, and from springs."
        "Energy from the sun and the force of gravity drive the continual movement of water between pools."
        "The sun’s energy causes liquid water to evaporate into water vapor."
        "Evapotranspiration is the main way water moves into the atmosphere from the land surface and oceans."
        "Gravity causes water to flow downward on land. It causes rain, snow, and hail to fall from clouds."

        Eight Terms (with definitions strictly traceable to the passage):
        1. Water Cycle: The system describing where water is on Earth and how it constantly moves.
        2. Evaporation: The process where the sun’s energy causes liquid water to turn into water vapor.
        3. Evapotranspiration: The main way water moves into the atmosphere from the land surface and oceans.
        4. Precipitation: Rain, snow, and hail that fall from clouds because of gravity.
        5. Runoff: The way water moves across the surface, along with snowmelt and streamflow.
        6. Infiltration: The way water moves into the ground.
        7. Groundwater Recharge: The process of water entering the ground to replenish underground supplies. (Or I can use Groundwater Discharge)
        8. Groundwater Discharge: The natural return of groundwater to the surface in rivers, the ocean, and from springs.
        9. Saline Water: Salty water, primarily stored in oceans, making up 96% of Earth's water.
        10. Fresh Water: Water stored in liquid form in lakes, rivers, and reservoirs, or as solid ice in glaciers and snowpack.

        Let's pick 10 definitions, giving at least 8.
        Perfect.

        **Human Influence**
        "Human water use, land use, and climate change all impact the water cycle."
        "The amount of water that is available depends on how much water there is in each pool, when and how fast water moves through the water cycle, and how clean the water is."
        "Water moves naturally and because of human actions."

        *Draft:*
        Human influence affects the water cycle through water use, land use, and climate change. These actions alter how water is stored, the timing and speed of its movement between pools, and the cleanliness of the water. Since water moves both naturally and because of human actions, recognizing these effects is essential for sustainable water management.

        Let's check if the prompt has any other constraints.
        "Do not introduce outside climate, policy, or regional examples."
        *My draft doesn't. It strictly summarizes the passage's general statements.*

        Let's perfectly format the answer.

        Overview:
        The water cycle describes the constant movement of water on Earth. Water is stored in oceans, the atmosphere, on the land surface, and underground. It can be liquid, solid, or gas. Solar energy and gravity drive the movement. Water circulates through evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Oceans, storing 96% of water, are saline, while the rest is freshwater in ice, lakes, rivers, and aquifers. Water availability depends on amounts in each pool, movement speed, and cleanliness. Human water use, land use, and climate change all impact the cycle.

        Concept Map:
        ```
        [Oceans] ----(Evaporation/Evapotranspiration)----> [Atmosphere]
             ↑                                                |
             |                                                | (Precipitation)
             |                                                v
             +-----------(Runoff/Streamflow)----- [Land/Ice] <+
                                                       |
                                                       | (Infiltration/Groundwater Recharge)
                                                       v
                                                 [Groundwater]
                                                       |
                                                       | (Groundwater Discharge)
                                                       v
                                              [Rivers, Springs, Oceans]
        ```

        Key Terms:
        1. Water cycle: The system describing where water is on Earth and how it constantly moves and changes form.
        2. Evaporation: The process by which the sun’s energy turns liquid water into water vapor.
        3. Evapotranspiration: The main pathway for water to move from the land surface and oceans into the atmosphere.
        4. Precipitation: Rain, snow, or hail that falls from clouds due to gravity.
        5. Runoff: The flow of water across the land surface toward streams and oceans.
        6. Infiltration: The process of water moving from the surface into the ground.
        7. Groundwater recharge: The process of infiltrating water entering and replenishing underground aquifers.
        8. Groundwater: Water that flows and is stored underground within aquifers.
        9. Groundwater discharge: The natural seepage of groundwater back to the surface into rivers, oceans, and springs.
        10. Saline water: Salty water that makes up 96% of Earth's water and is mostly stored in oceans.

        Human influence:
        Human actions including water use, land use, and climate change impact the water cycle by altering water movement, storage, and availability. The amount of water in each pool, the speed of its movement through the cycle, and its cleanliness can all be affected. Because water moves both naturally and through human actions, understanding these impacts is required to use water sustainably.

        Looks solid. No outside knowledge. All facts from the passage. Follows structure. Included more than 8 terms!
        Ready to output.
````

## Assistant

````markdown
Here is the structured summary based solely on the provided USGS passage.

### 1. Concise 100-word Overview
The water cycle describes the constant movement of water on Earth. Water is stored in oceans, the atmosphere, on the land surface, and underground, existing as a liquid, solid, or gas. Solar energy and gravity drive this movement through evaporation, evapotranspiration, precipitation, runoff, infiltration, and groundwater flow. Oceans hold 96% of Earth’s water as saline water; the rest is freshwater in ice, lakes, rivers, and aquifers. The amount of available water depends on the volume in each pool, the speed of movement, and water cleanliness. Human water use, land use, and climate change all impact this cycle.

### 2. Concept Map
```
[Oceans] ----(Evaporation / Evapotranspiration)----> [Atmosphere]
     ↑                                                        |
     |                                                        | (Precipitation)
     |                                                        v
     +-----------(Runoff / Streamflow)-------- [Land / Ice] <+
                                                    |
                                                    | (Infiltration / Groundwater Recharge)
                                                    v
                                              [Groundwater]
                                                    |
                                                    | (Groundwater Discharge)
                                                    v
                                         [Rivers, Springs, Oceans]
```

### 3. Key Terms
1.  **Water cycle**: The system describing where water is on Earth and how it constantly moves and changes form.
2.  **Evaporation**: The process where the sun’s energy causes liquid water to turn into water vapor.
3.  **Evapotranspiration**: The main way water moves into the atmosphere from the land surface and oceans.
4.  **Precipitation**: Rain, snow, and hail that fall from clouds because of the force of gravity.
5.  **Runoff**: The movement of water across the land surface, including snowmelt and streamflow.
6.  **Infiltration**: The process of water moving from the surface into the ground.
7.  **Groundwater recharge**: The process of water moving into the ground to replenish underground aquifers.
8.  **Groundwater**: Water that is stored underground and flows within aquifers.
9.  **Groundwater discharge**: The natural return of groundwater to the surface in rivers, the ocean, and from springs.
10. **Saline water**: Salty water that is primarily stored in oceans, which store 96% of all water on Earth.

### 4. Human Influence
Human water use, land use, and climate change all impact the water cycle. The amount of water available for life depends on how much is in each pool, when and how fast water moves between pools, and how clean the water is. Because water moves both naturally and as a direct result of human actions, understanding these impacts is necessary to work toward using water sustainably.
````
