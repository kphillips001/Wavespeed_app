from app.prompts.shot_types import SHOT_TYPES


def build_premium_shot_type_context():
    formatted_shot_types = "\n".join(
        f"- {shot_type}"
        for shot_type in SHOT_TYPES
    )

    return f"""
SHOT INTELLIGENCE:
Use a natural mix of creator photography shot types.

Suggested shot types:
{formatted_shot_types}

IMPORTANT:
- These are not rigid rules.
- Adapt shot types naturally to the user's creative tags.
- Avoid repeating the same framing repeatedly.
- Vary visual energy across the batch.
- Build visually different creator moments.

Use these to vary:
- pose
- framing
- camera distance
- body orientation
- perspective
- camera height
- emotional tone
- closeups vs full-body shots
- environmental interaction
- storytelling energy
"""


def build_premium_grok_prompt(
    creative_tags: str,
    prompt_count: int = 10,
) -> str:

    shot_type_context = build_premium_shot_type_context()

    return f"""
I need a list of {prompt_count} high-quality WAN 2.7 image-edit prompts.

These prompts always use the SAME reference image.

Every prompt MUST preserve:
- same woman
- same face
- same hair
- same identity from the reference image
- same general skin tone
- same creator aesthetic
- same overall attractiveness
- same recognizable body structure

Body Preservation Rules:
- preserve overall identity
- maintain realistic anatomy
- maintain feminine proportions
- maintain healthy curves
- preserve photorealistic body structure
- preserve recognizable body shape
- avoid exaggerated anatomy
- avoid unrealistic proportions
- avoid artificial body distortion

USER CREATIVE TAGS:
{creative_tags}

MANDATORY TAG ENFORCEMENT:

User Creative Tags are mandatory.

Do NOT reinterpret, soften, replace, weaken, or remove user tags.

Every prompt MUST contain all requested creative tags.

Examples:

If user enters:
nude, luxury apartment, evening

EVERY prompt must contain:
- fully nude subject
- luxury apartment environment
- evening atmosphere

If user enters:
bare breasts, beach, sunset

EVERY prompt must contain:
- visible bare breasts
- beach environment
- sunset lighting

If user enters:
bikini, lake, summer

EVERY prompt must contain:
- bikini
- lake environment
- summer atmosphere

The user tags define the core content of every image.

Only vary:
- pose
- camera angle
- framing
- expression
- body language
- storytelling moment
- environment details
- lighting nuances
- micro-action
- viewer connection

Never replace requested nudity with:
- dresses
- crop tops
- lingerie
- robes
- slips
- swimsuits
- implied nudity
- partially clothed alternatives

when the user explicitly requests:
- nude
- nudity
- naked
- topless
- bare breasts

Requested nudity must remain visible in every prompt.

NUDITY CONSISTENCY RULE:

If the user requests:
- nude
- nudity
- naked
- topless
- bare breasts

then EVERY prompt must contain visible nudity.

Do not alternate between clothed and nude images.

Do not create outfit variations.

Do not replace nudity with:
- dresses
- crop tops
- lingerie
- slips
- robes
- swimsuits
- partially clothed alternatives

unless explicitly requested by the user.

Visible nudity is mandatory in every prompt.

PREMIUM CREATIVE DIRECTOR MODE:

The user is NOT writing full prompts.
The user is only providing creative signals.

Your job is to become a Premium AI Creative Director.

Turn short premium tags into complete WAN 2.7 image-edit prompts.

These prompts are intended for premium creator-content generation.

CORE OBJECTIVE:

The images should feel like authentic premium creator content.

The viewer should feel:

"I am sharing a private moment with her."

NOT:

"I am looking at a professional photoshoot."

The images should feel:
- intimate
- alluring
- seductive
- flirtatious
- confident
- playful
- inviting
- realistic
- personal
- authentic
- emotionally engaging
- captured in the moment
- private
- subscriber-focused

PREMIUM CREATOR CONTENT PHILOSOPHY:

The environment is NOT the main subject.

The woman is always the main subject.

Mountains, lakes, beaches, cabins, hotels, rooftops, pools, resorts, city views, apartments, and travel locations should support the scene rather than dominate it.

The viewer should feel:

"I am sharing this moment with her."

NOT:

"I am looking at a landscape that happens to contain a woman."

SUBSCRIBER POV:

The image should feel like content intended for a paying subscriber.

The viewer should feel:
- she is sharing this moment with me
- she knows I am watching
- she is intentionally inviting attention
- she feels approachable
- she feels real
- the moment feels private
- the image feels personal, not commercial
- she is comfortable around the viewer
- she is letting the viewer into her private evening

Avoid:
- luxury real estate photography
- travel brochure photography
- commercial advertising
- fashion campaign imagery
- catalog posing
- studio glamour photography
- professional photoshoot energy
- magazine editorial energy

SEXUAL TENSION:

The goal is attraction.

Use:
- subtle seduction
- flirtatious body language
- teasing posture
- inviting eye contact
- confident femininity
- playful attraction
- alluring expressions
- viewer engagement
- soft sensuality
- relaxed confidence
- natural body language
- warm private energy
- quiet erotic tension
- personal connection

Avoid:
- emotionless posing
- blank expressions
- detached body language
- catalog posing
- stiff model posing
- cold fashion energy
- overdone glamour posing

ADULT PREMIUM CONTENT DIRECTION:

If the user's creative tags include nude, nudity, naked, bare, topless, bare breasts, shower, wet, bedroom, implied private moment, or similar premium-content signals, include tasteful adult nudity directly in the prompts.

Use clear visual language such as:
- fully nude
- natural nudity
- topless
- bare breasts visible
- bare shoulders and chest
- intimate nude creator moment
- private nude vacation moment
- tasteful nude body language
- confident nude pose
- alluring nude expression
- nude private evening moment
- nude apartment moment
- nude bedroom moment

Keep the scene focused on:
- her expression
- eye contact
- body language
- intimacy
- viewer connection
- realism
- natural creator energy
- private-moment feeling

Do NOT make the scene clinical, pornographic, or detached.

Do NOT describe explicit sexual acts.

Do NOT include sex acts, penetration, fluids, fetish language, or graphic sexual details.

The goal is:
premium nude creator content,
not explicit sex-scene prompting.

Visual Preferences:
- close creator-style framing
- intimate camera distance
- strong subject focus
- natural eye contact
- teasing eye contact
- playful expressions
- alluring facial expressions
- relaxed confidence
- natural body language
- realistic weight shifts
- body-leading composition
- flattering camera angles
- authentic creator-content energy
- premium smartphone-camera realism
- realistic skin texture
- warm skin glow
- believable lighting
- natural depth of field
- environmental depth without overwhelming the subject
- visually engaging silhouettes
- emotionally engaging moments
- private creator-content realism
- natural social-media creator energy
- intimate lifestyle storytelling
- natural smartphone-photo realism
- private apartment atmosphere when indoors

VIEWER CONNECTION:

The viewer should feel personally noticed.

Favor:
- direct eye contact
- glancing toward camera
- looking back over shoulder
- playful eye contact
- teasing smile
- inviting expression
- soft smirk
- relaxed smile
- confident gaze
- warm expression
- slight parted-lip expression
- subtle flirtatious expression

Avoid:
- staring into distance in every image
- looking away in every image
- disconnected expressions
- emotionless expressions
- blank face
- cold model stare
- lifeless posing

INTIMATE CREATOR MOMENTS:

These images should feel like authentic creator content.

Favor:
- relaxing on a bed
- sitting on a kitchen island
- sitting on a couch
- reclining on furniture
- sitting on a window ledge
- relaxing beside large windows
- leaning against a counter
- walking barefoot through an apartment
- looking back toward camera
- playful eye contact
- soft teasing expressions
- confident feminine energy
- candid private lifestyle moments
- relaxing in a bedroom
- sitting near city-view windows
- standing near warm apartment lighting
- resting against furniture naturally
- captured mid-moment
- private evening moments
- quiet night-in moments
- bedroom evening moments
- kitchen island moments
- window ledge moments
- couch lounging moments

The viewer should feel:

"I just walked into the room."

Avoid:
- runway fashion energy
- commercial advertisements
- studio photography
- corporate stock photography
- stiff posing
- fashion catalog imagery
- staged hotel marketing energy

PRIVATE MOMENT PRIORITIES:

The image should feel like a private moment that happened naturally.

Favor:
- relaxing on a bed
- sitting on a kitchen island
- sitting on a couch
- lounging on a chair
- sitting on a window ledge
- resting against a countertop
- leaning into furniture
- stretching naturally
- relaxing after a shower
- adjusting hair
- pulling a blanket closer
- resting one hand on a thigh
- crossing legs naturally
- shifting position casually
- sitting barefoot
- relaxing while looking toward camera
- glancing over shoulder
- settling into furniture
- enjoying a quiet evening indoors
- sitting beside large windows
- enjoying city lights
- relaxing during a private evening

Reduce heavily:
- standing poses
- runway poses
- fashion poses
- walking poses
- model poses
- symmetrical poses
- distant full-body standing shots

The image should feel lived-in rather than posed.

MICRO-ACTION PRIORITY:

The subject should usually be engaged in a small natural action.

Favor:
- brushing hair behind one ear
- adjusting her hair
- leaning forward slightly
- shifting her weight naturally
- settling into a chair
- pulling a blanket closer
- looking back over her shoulder
- resting an elbow on a counter
- sitting cross-legged
- relaxing against a window
- resting her chin lightly on a hand
- adjusting a sheet
- stretching gently
- glancing toward camera mid-movement
- relaxing into furniture
- sitting on a countertop
- climbing onto a bed
- resting her elbows on a balcony rail
- sitting on a window ledge
- resting one hand on her thigh

Avoid:
- frozen posing
- perfectly symmetrical posing
- catalog posing
- pageant posing
- runway posing
- mannequin-like posing

The image should feel like a captured moment.

POSE PRIORITIES:

Favor:
- reclining
- lounging
- sitting
- resting
- stretching naturally
- leaning
- kneeling naturally
- sitting on countertops
- sitting on beds
- sitting on couches
- sitting on window ledges
- crossing legs naturally
- resting one hand naturally on furniture
- leaning one hip against a counter
- relaxing into the environment
- casual body positioning
- bed-edge poses
- couch-edge poses
- window-seat poses
- kitchen-island poses

Reduce:
- standing poses
- runway poses
- fashion poses
- model-walk poses
- distant full-body standing shots
- stiff symmetrical poses

BODY PRESENTATION:

When nudity is requested, favor:
- visible cleavage
- visible breasts
- natural breast presentation
- bare breasts visible when requested
- flattering upper-body angles
- body-leading composition
- feminine curves
- natural nude body language
- warm skin glow
- realistic skin texture
- intimate body orientation
- natural relaxed posture

Maintain realism.

Avoid:
- exaggerated anatomy
- cartoon proportions
- distorted bodies
- unnatural body shapes

INTIMACY PRIORITY RULE:

The strongest premium creator content feels physically close.

Favor heavily:

- lying on a bed
- sitting on a bed
- lounging on a couch
- reclining on furniture
- sitting in a chair
- resting on a fireplace rug
- sitting on a kitchen island
- leaning across a countertop
- sitting on a window seat
- sitting beside a fireplace
- relaxing beneath blankets
- leaning toward camera
- lying on stomach
- lying on side
- seated close-up portraits
- upper-body focused compositions
- chest-up compositions
- waist-up compositions
- intimate close framing

Reduce heavily:

- standing in rooms
- standing beside walls
- standing by windows
- standing in hallways
- standing in kitchens
- standing in bedrooms
- fashion-style standing poses
- model-style standing poses
- distant full-body shots

The viewer should feel:

"I am sitting beside her."

NOT:

"I am looking across the room at her."

PROXIMITY RULE:

The viewer should feel physically close to her.

Favor:
- close-up portraits
- chest-up framing
- waist-up framing
- upper-thigh framing
- seated close framing
- intimate couch framing
- intimate bed framing
- bed-edge framing
- countertop framing
- balcony railing framing
- kitchen island framing
- window ledge framing
- over-the-shoulder perspectives
- subject filling most of the frame

Limit:
- distant full-body shots
- large empty rooms
- excessive floor space
- excessive ceiling space
- architecture-focused compositions
- wide room establishing shots
- real-estate photography compositions
- tiny subject compositions

The woman should occupy most of the frame.

PERSONAL CONTENT PRIORITY:

These images should resemble:

- premium subscriber content
- private creator content
- girlfriend experience content
- candid vacation moments
- personal weekend moments
- intimate lifestyle content

The image should feel:

- personal
- close
- private
- authentic
- emotionally engaging

The woman should feel more important than the environment.

When deciding between:

A) showing more scenery

or

B) showing more of her face, expression, body language, and eye contact

always choose B.

INTIMACY OVERRIDES VARIETY:

When generating prompt variation:

DO NOT prioritize creating entirely different scenes.

Instead prioritize creating different intimate moments within the same environment.

Example:

Pool environment:
- sitting on pool edge
- reclining on pool edge
- seated in shallow water
- leaning on pool coping
- resting arms on pool edge
- floating close to camera
- seated on submerged steps
- lounging beside water
- looking toward camera from water level
- relaxing with legs in pool

Do NOT force:
- standing poses
- distant environmental shots
- architecture showcases
- travel photography angles

The goal is multiple intimate moments,
not multiple locations.

CAMERA DIRECTION:

Favor:
- close-up portraits
- close-medium framing
- waist-up framing
- upper-thigh framing
- seated intimate framing
- over-the-shoulder perspectives
- eye-level camera angles
- slightly low camera angles
- candid creator-camera perspectives
- natural handheld camera feeling
- realistic social-media photography
- camera positioned close enough to feel personal
- subject filling most of the frame
- smartphone camera realism
- personal-distance camera placement
- casual handheld framing
- slightly imperfect crop when natural

Avoid:
- distant full-body landscape shots
- tiny subject in large scenery
- travel-poster compositions
- environment-first compositions
- overly editorial framing
- magazine-cover styling
- fashion-runway energy
- wide empty room compositions
- architecture-focused framing

PREMIUM SUBSCRIBER CONTENT:

Generate moments that feel like content a creator would share privately with a subscriber.

Examples:
- relaxing before bed
- waking up slowly
- lounging after a shower
- sitting on a kitchen island at night
- enjoying city lights from a window
- sitting beside a balcony window
- relaxing on a couch
- reading in bed
- stretching after waking up
- wrapped loosely in bedding
- enjoying a quiet evening indoors
- relaxing during a private vacation
- watching the sunset from a balcony
- enjoying a secluded cabin evening
- relaxing beside a fireplace
- sitting barefoot near warm apartment lighting
- leaning against a counter during a quiet night in
- sitting on a bed while looking toward the camera
- relaxing near large windows with city lights behind her

The image should feel personal, intimate, and authentic.

The viewer should feel:

"I am sharing this moment with her."

PREMIUM MOMENT DESIGN:

Create scenes that feel like:
- private vacation moments
- personal travel moments
- intimate lakeside moments
- secluded mountain getaway moments
- relaxing cabin moments
- quiet sunset moments
- playful beach moments
- private rooftop moments
- candid creator moments
- spontaneous lifestyle moments
- private apartment moments
- bedroom evening moments
- kitchen island moments
- window ledge moments
- couch lounging moments
- quiet night-in moments

The viewer should feel like they accidentally caught a beautiful private moment.

INTIMATE CAMERA DISTANCE:

The camera should feel within arm's reach of the woman.

Favor heavily:

- close-up
- medium close-up
- waist-up
- upper-thigh framing
- seated close framing
- reclining close framing
- bed-level perspective
- eye-level perspective
- viewer sitting beside her

Avoid:

- camera positioned across the room
- camera positioned across the pool
- distant environmental perspectives
- wide establishing shots
- drone-like perspectives
- scenery-focused framing

The viewer should feel physically present.

EXPRESSION GUIDANCE:

Frequently use:
- soft smile
- teasing smile
- playful grin
- flirtatious glance
- looking back toward camera
- glancing over shoulder
- subtle smirk
- relaxed expression
- dreamy expression
- confident expression
- inviting eye contact
- slight parted-lip expression
- warm eye contact
- playful confidence
- private smile
- soft mischievous look
- relaxed bedroom expression
- quiet confident gaze

Avoid:
- neutral expression in every prompt
- blank face
- cold model stare
- overly staged glamour expression
- emotionless face

Body and Appearance Guidance:
- preserve exact facial identity
- preserve recognizable body shape
- maintain realistic anatomy
- maintain healthy feminine proportions
- maintain natural curves
- preserve an enhanced hourglass silhouette
- preserve a fuller upper-body appearance while remaining realistic
- use flattering posture
- use flattering body orientation
- create visually appealing silhouettes through composition
- avoid distorted anatomy
- avoid exaggerated anatomy
- maintain photorealistic body structure

REALISM / CAUGHT-IN-THE-MOMENT PRIORITIES:

TOP PRIORITY:
The image should feel like a real creator moment captured naturally.

The viewer should feel:

"I caught this private moment"

NOT:

"she stopped for a staged photoshoot."

Use realism through:
- candid timing
- imperfect posture
- natural weight shifting
- casual body positioning
- small facial asymmetry
- relaxed expressions
- slight movement where natural
- hair partially out of place
- natural hand placement
- mid-motion behavior
- glancing toward camera instead of staring every time
- natural breathing posture
- relaxed spine positioning
- sitting naturally
- leaning naturally
- body resting against environment
- captured between actions
- natural phone-camera feeling
- subtle body movement
- natural asymmetry
- realistic relaxed posture
- organic hand placement

REAL CAMERA FEEL:

The photo should feel like a real creator casually took the image.

Use:
- smartphone camera realism
- handheld feeling
- casual framing
- slight camera tilt sometimes
- slightly imperfect crop
- realistic social-media composition
- natural depth of field
- occasional foreground objects
- realistic phone-camera sharpness
- natural subject placement
- image captured between moments
- candid timing
- authentic creator-content feeling

Avoid:
- centered fashion framing
- magazine composition
- studio energy
- perfectly symmetrical placement
- runway photography
- professional campaign feeling
- commercial product photography
- real-estate style room photography

{shot_type_context}

PROMPT REQUIREMENTS:
- Return exactly {prompt_count} prompts
- Number the prompts
- Each prompt must be substantially different
- Use different shot types throughout the batch
- Use different camera angles throughout the batch
- Use different environments throughout the batch
- Use different poses throughout the batch
- Preserve the same woman in every image
- Write complete WAN 2.7 image-edit prompts
- Each prompt should feel close, personal, realistic, and creator-captured
- Each prompt should prioritize the woman over the scenery
- Each prompt should include an expression or viewer-connection detail
- Each prompt should include body language or a natural micro-behavior
- Each prompt should include camera distance or framing
- Each prompt should include lighting

- At least 90% of prompts should use:
  - seated poses
  - reclining poses
  - lounging poses
  - resting poses
  - bed poses
  - couch poses
  - chair poses
  - fireplace poses
  - floor-rug poses
  - kitchen-island poses
  - countertop poses
  - window-seat poses
  - intimate close-up poses
  - personal lifestyle moments

- No more than 10% of prompts should use standing poses

- Favor:
  - close-up framing
  - chest-up framing
  - waist-up framing
  - upper-thigh framing
  - intimate seated framing
  - bed-edge framing
  - couch-edge framing
  - kitchen-island framing
  - window-seat framing
  - over-the-shoulder perspectives
  - subject-dominant compositions

- The woman should occupy 60-90% of the frame

- The environment should support the scene rather than dominate it

- Do not generate:
  - environment-first compositions
  - architecture-first compositions
  - real-estate photography compositions
  - landscape-first compositions
  - travel-poster compositions
  - distant full-body room shots
  - tiny-subject compositions

- The viewer should feel:
  - physically close to her
  - personally noticed
  - included in the moment
  - invited into a private experience

- The image should feel:
  - personal
  - intimate
  - authentic
  - subscriber-focused
  - emotionally engaging
  - naturally captured

- The image should resemble:
  - premium creator content
  - private lifestyle content
  - candid creator moments
  - girlfriend-experience style photography
  - personal vacation moments
  - quiet evening moments
  - relaxed weekend moments

- Every prompt should feel like a personal creator moment rather than a professional photoshoot

- When choosing between:
  A) showing more scenery
  B) showing more of her face, expression, body language, and eye contact

  Always choose B.

- Favor prompts involving:
  - lying on a bed
  - sitting on a bed
  - lounging across a couch
  - reclining in a chair
  - relaxing beside a fireplace
  - seated on a kitchen island
  - leaning across a countertop
  - curled beneath blankets
  - seated beside a window
  - resting on a fur rug
  - intimate bedroom moments
  - candid evening moments

- Avoid repeatedly generating:
  - standing beside windows
  - standing in rooms
  - standing beside walls
  - standing in hallways
  - standing in kitchens
  - standing beside furniture
  - fashion-model standing poses
  - catalog-style posing

- If nudity is requested in the user tags, include tasteful nudity clearly in every prompt

- If topless or nude content is requested, include natural nudity directly in every prompt

- If nudity is requested, do not alternate between clothed and unclothed prompts

- If nude, nudity, naked, topless, or bare breasts are requested, do not include clothing or outfit alternatives unless explicitly requested by the user

- Do not include explanations
- Do not include introductions
- Do not include summaries
- Output prompts only
"""