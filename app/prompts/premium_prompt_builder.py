from app.prompts.shot_types import SHOT_TYPES


def build_nsfw_progression_instruction(prompt_count: int = 10) -> str:
    return f"""
AUTOMATIC FULL NSFW PROGRESSION MODE (HIGH PRIORITY):

When the reference image shows partial nudity (topless, lingerie, bra/panties, sheer clothing, etc.) or the creative tags suggest NSFW/premium adult content, automatically create a strong, natural erotic evolution story across the entire batch.

Progression flow (spread naturally across the {prompt_count} prompts):
1. Start very close to the reference pose/setting
2. Increase sensuality: hands on breasts, squeezing, playing with nipples
3. Touching lower body over clothing (rubbing panties, hand between legs)
4. Progressive clothing removal (sliding panties down, fully removing them)
5. Full nude with legs opening/spreading
6. Explicit intimate self-touch: fingers rubbing clit, fingering, masturbation poses
7. Various angles, pleasure expressions (eyes closed in ecstasy, biting lip, moaning face, etc.)

MANDATORY RULES:
- Stay in the EXACT same environment, lighting, floor/walls/background/furniture as the reference image. Do NOT change the location.
- Never revert to more clothing than the reference.
- Keep perfect face, hair, body, tan, and D-cup bust continuity in EVERY prompt.
- Increase explicitness gradually across the batch.
- Use natural, sensual, private-creator-moment language.
"""


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
    optional_direction: str | None = None,
) -> str:

    shot_type_context = build_premium_shot_type_context()
    nsfw_progression = build_nsfw_progression_instruction(prompt_count)
    direction_text = (optional_direction or "").strip()

    direction_instruction = (
        f"""
OPTIONAL SETTING / DIRECTION:
The user supplied this setting/framing direction:
{direction_text}

Treat this as mandatory creative direction for the whole batch.
If it includes framing language such as full body, wide shot, environmental shot,
mirror selfie, waist-up, close-up, medium shot, or upper-thigh framing, follow that
framing direction even when it differs from the default close-framing preference.
Still preserve her full natural D-cup bust, feminine hourglass body, same
waist-to-hip proportions, rich dark tan skin, and recognizable body structure.
"""
        if direction_text
        else """
OPTIONAL SETTING / DIRECTION:
No additional direction supplied. Rely on automatic NSFW progression.
"""
    )

    return f"""
I need a list of {prompt_count} high-quality WAN 2.7 image-edit prompts.

These prompts always use the SAME reference image.

{nsfw_progression}

Every prompt MUST preserve:
- same woman
- same face
- same hair
- same identity from the reference image
- same general skin tone, with a rich dark tan
- same creator aesthetic
- same overall attractiveness
- same recognizable body structure

Body Preservation Rules:
- preserve overall identity
- maintain realistic anatomy
- maintain feminine proportions
- maintain healthy curves
- maintain a nice dark tan across the visible skin
- preserve photorealistic body structure
- preserve recognizable body shape
- avoid exaggerated anatomy
- avoid unrealistic proportions
- avoid artificial body distortion

Skin Tone Rules:
- every final prompt must explicitly include rich dark tan skin
- preserve the same rich dark tan across face, chest, arms, waist, hips, and legs when visible
- keep the tan natural, even, sun-kissed, and photorealistic
- do not make her pale, red-haired, washed out, or fair-skinned
- do not change her underlying identity or facial features while emphasizing the dark tan

Bust Consistency Rules:
- preserve the exact bust size shown in the reference image
- maintain full natural D-cup breast proportions
- maintain the exact breast size visible in the reference image
- preserve full breast volume and projection
- preserve natural D-cup fullness across every prompt
- maintain visible breast projection
- maintain visible D-cup bust projection through wardrobe, pose, camera angle, and framing
- maintain full upper breast volume
- maintain full lower breast volume
- maintain rounded natural breast shape
- maintain natural cleavage when visible
- maintain consistent nipple size and placement when topless or nude
- maintain naturally visible nipples when topless or nude
- nipples should remain unobstructed when topless
- nipples should be clearly visible whenever topless is requested
- do not reduce breast volume
- do not make the subject smaller-busted than the reference image
- do not flatten the chest
- do not make the breasts look like a small B cup
- keep bust proportions consistent across every prompt

Premium Body Output Requirement:
- Every final prompt must explicitly include her same full natural D-cup bust.
- Every final prompt must explicitly include her same feminine hourglass body.
- Every final prompt must explicitly include her same waist-to-hip proportions.
- Every final prompt must explicitly include rich dark tan skin.
- Every final prompt must preserve and visibly reference her same recognizable body structure.
- The D-cup bust requirement is mandatory in every returned prompt.
- Never reduce, soften, omit, or generalize the D-cup bust requirement.
- Do not say only "curvy" or "attractive"; explicitly write full natural D-cup bust.
- Do not make body preservation implicit only.
- Do not omit the D-cup bust or hourglass body continuity from the final prompt text.
- For clothed or lingerie prompts, preserve the body through fitted wardrobe, natural cleavage when visible, bust projection through fabric, flattering posture, and close-medium framing.
- Use premium-safe wording such as:
  - full natural D-cup bust
  - feminine hourglass body
  - same curvy waist-to-hip proportions
  - rich dark tan skin
  - fitted premium styling that preserves her bust and body shape
  - visible D-cup bust projection through the outfit

Premium Framing Requirement:
- Favor closer creator-style framing over distant scenery.
- Most prompts should use close-up, close-medium, waist-up, upper-thigh, or head-to-thigh framing.
- Keep her body large in frame, with the background supporting the scene rather than dominating it.
- Avoid distant full-body compositions unless the user specifically asks for a wide environmental shot.
- Do not crop out the body cues needed to preserve her D-cup bust, hourglass shape, and tan skin.

Premium Prompt Detail Contract:
Every returned premium prompt must be as detailed and concrete as an explicit prompt, but remain premium/teasing unless the user specifically requests nude/topless content.

Each prompt must include:
- exact reference identity preservation
- full natural D-cup bust
- feminine hourglass body
- same waist-to-hip proportions
- rich dark tan skin
- wardrobe or lingerie details
- pose and body orientation
- camera angle
- shot distance and crop
- expression or viewer connection
- hand placement or natural micro-behavior
- lighting quality
- background/environment details
- skin, hair, fabric, and texture realism
- premium creator-content realism
- photorealistic image-generation detail

For lingerie, teasing, or premium non-nude prompts:
- use fitted lingerie, sheer robe, bodysuit, fitted sleepwear, bikini, crop top, shorts, or other user-requested wardrobe only when appropriate
- preserve D-cup bust projection through clothing or lingerie
- show natural cleavage when wardrobe/framing allows it
- keep the prompt sensual, intimate, premium, and realistic
- do not include explicit sexual acts
- do not include graphic genital detail
- do not make the content fully nude unless the user tags specifically request nude, naked, topless, or bare breasts

USER CREATIVE TAGS:
{creative_tags}

{direction_instruction}

IMPORTANT:

Treat user tags as a theme.

Do NOT copy the enhanced tags literally.

Extract the core idea and create multiple scene concepts.

Example:

topless, pool, night

does NOT mean:

10 prompts beside the same pool.

It means:

10 completely different premium moments
that all happen to include a pool at night.

Generate scene variety first.

MANDATORY TAG ENFORCEMENT:

User Creative Tags are mandatory.

CRITICAL NUDITY / CLOTHING ENFORCEMENT:

ABSOLUTE PRIORITY RULE:

User creative tags override every other instruction in this document.

Be creative only with:
- pose
- camera angle
- framing
- expression
- lighting
- environment details
- mood
- micro-action

Do NOT be creative with required user tags.

If the user requests topless, bare breasts, nude, naked, booty shorts, bikini, lake, couch, bedroom, shower, or any specific wardrobe/location, preserve those exact requirements in every prompt.

If the user requests topless:

EVERY prompt must include:

TOPLESS,
bare breasts clearly visible,
natural nipples visible,
no bra,
no lingerie top,
no shirt,
no crop top,
no dress,
no robe,
no swimsuit,
no bikini top,
no upper-body clothing.

Topless enforcement rules:

- bare breasts must remain visible
- nipples should remain naturally visible
- hair should not completely cover the chest
- arms should not completely cover the breasts
- framing should clearly show the topless state
- avoid poses that hide the chest from the camera
- avoid camera angles that obscure the breasts
- avoid furniture, blankets, pillows, or objects covering the breasts
- the viewer should immediately recognize that the subject is topless
- topless visibility must be preserved in every prompt

If the user requests:

- nude
- nudity
- naked
- completely nude
- fully nude

EVERY prompt must include:

COMPLETELY NUDE,
bare breasts visible,
natural nipples visible,
no clothing.

Nudity enforcement rules:

- no bras
- no lingerie
- no lingerie tops
- no shirts
- no crop tops
- no robes
- no bikinis
- no swimsuits
- no dresses
- no towels covering the body

The subject must remain completely nude.

Avoid:

- implied nudity
- hidden nudity
- obscured nudity
- covered breasts
- cropped-away nudity

The viewer should immediately recognize the subject is completely nude.

If the user requests booty shorts:
EVERY prompt must include:
wearing ONLY booty shorts on the lower body.

Never substitute requested clothing or nudity with lingerie, dresses, slips, bodysuits, swimsuits, robes, or implied nudity.

If the user tags include topless, every prompt must explicitly say:
TOPLESS, bare breasts fully visible, no bra, no lingerie top, no shirt, no crop top, no dress, no robe, no upper-body clothing.

If the user tags include nude, nudity, or naked, every prompt must explicitly say:
FULLY NUDE, no clothing, bare breasts visible, bare body visible.

If the user tags include booty shorts, every prompt must explicitly say:
wearing ONLY booty shorts on the lower body.

Never replace user-requested topless, nude, or bare breasts with:
- lingerie
- black satin lingerie
- dresses
- slips
- bodysuits
- swimsuits
- bras
- crop tops
- shirts
- robes
- covered breasts
- implied nudity

Never add upper-body clothing when the user requested topless or bare breasts.

Never add dresses, lingerie, slips, or bodysuits unless the user explicitly requested them.

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
- maintain the exact bust proportions shown in the reference image
- maintain full natural D-cup breast volume
- maintain substantial upper-breast fullness
- maintain substantial lower-breast fullness
- maintain visible breast projection
- maintain noticeable breast projection
- maintain full upper breast fullness
- maintain full lower breast fullness
- maintain the same breast volume visible in the reference image
- maintain the same breast projection visible in the reference image
- maintain the same chest-to-waist proportions visible in the reference image
- maintain full natural breast mass
- maintain rounded full breast contours
- maintain natural upper breast fullness
- preserve bust size from the reference image
- preserve breast shape from the reference image
- maintain rounded natural breast shape
- maintain consistent breast width and spacing
- maintain natural cleavage when visible
- nipples should remain naturally visible when topless
- nipples should not be obscured by hair
- nipples should not be obscured by arms
- nipples should not be obscured by furniture
- maintain natural nipple visibility consistent with the reference image
- maintain consistent nipple placement

- maintain the exact overall body proportions shown in the reference image
- maintain the same overall body shape
- maintain the same overall body weight and physique
- maintain the same waist-to-hip ratio
- maintain the same hip width
- maintain the same thigh thickness
- maintain the same leg proportions
- maintain the same shoulder width
- maintain the same feminine hourglass silhouette
- maintain consistent body proportions across every generated image

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
- reducing breast volume
- reducing breast projection
- reducing breast fullness
- flattening the chest
- making the subject smaller-busted than the reference image
- small B-cup interpretations
- minimizing breast volume
- athletic chest reinterpretations
- flatter chest interpretations
- reducing bust size from the reference image
- inconsistent breast size across prompts

- changing body weight
- changing waist size
- changing hip size
- changing thigh thickness
- changing shoulder width
- changing overall body proportions
- changing chest-to-waist proportions
- changing bust-to-waist proportions
- altering the recognizable silhouette of the reference image

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

CREATIVE VARIETY OVERRIDES REPETITION:

Premium Studio is an IDEA GENERATOR.

This is NOT a photoshoot sequence.

This is NOT a continuity series.

This is NOT a scene progression.

Every prompt should feel like a completely different premium image concept.

The user's tags define REQUIRED ELEMENTS and a BROAD THEME.

The user's tags do NOT require every prompt to stay in the exact same room, corner, furniture setup, or micro-location.

Extract:

- wardrobe requirements
- nudity requirements
- broad setting theme
- atmosphere requirements

Then generate completely different visual scenarios.

If the user gives a broad setting like:
- indoors
- outdoors
- hotel lounge
- apartment
- bedroom
- cabin
- pool
- porch
- city
- beach
- lake

you may expand into nearby or related settings that fit the same theme.

Example:

hotel lounge can expand into:
- hotel lounge sofa
- penthouse suite
- private hotel balcony
- upscale hotel bedroom
- luxury bathroom mirror
- cocktail bar corner
- high-rise window seat
- hotel hallway doorway
- private terrace
- hotel room couch

Do NOT repeat the same exact location across the batch.

Example:

fireplace, crop top, booty shorts

Required elements:

- fireplace
- crop top
- booty shorts

DO NOT repeat the same fireplace scene.

Create different interactions around the fireplace.

Example concepts:

- sitting on hearth
- lying on rug
- sitting in chair beside fireplace
- leaning on mantel
- curled up on couch
- standing in doorway
- sitting on floor
- stretching beside fireplace
- window seat near fireplace
- reading beside fireplace

The required elements remain.

The scene must change.

Example:

If user enters:

nude, pool, night

Valid prompt concepts include:

- standing beside pool
- floating in water
- submerged pool steps
- outdoor shower
- poolside lounge chair
- hot tub
- cabana seating
- pool bar
- fire pit area
- balcony overlooking pool
- poolside daybed
- pool staircase
- indoor pool
- infinity edge
- private resort room overlooking pool

Do NOT generate ten images in the same location.

The environment should change naturally while preserving the user theme.

Example:

If user enters:

topless, porch, night

Valid concepts include:

- leaning on railing
- sitting in rocking chair
- sitting on porch swing
- standing in doorway
- sitting on porch steps
- relaxing on outdoor couch
- sitting on bench
- wrapped in blanket on porch chair
- leaning against porch column
- standing near screen door

Do NOT repeatedly use:

- same railing
- same chair
- same corner
- same furniture
- same camera position

Every prompt must begin from a different visual concept.

MANDATORY VARIETY:

Across the batch intentionally vary:

- environment location
- furniture
- architecture element
- interaction point
- activity
- pose
- body orientation
- camera angle
- framing
- perspective
- expression
- storytelling moment

Changing only:

- smile
- eye direction
- hand placement

does NOT count as variation.

Every prompt should feel like a different premium image that could have been posted on a different day.

AVOID:

- same location repeated
- same furniture repeated
- same pose repeated
- same framing repeated
- same environmental interaction repeated

Generate genuine variety.

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

PHONE CAMERA REALISM PRIORITY:

The image should feel like she personally took this for a subscriber.

Favor:

- smartphone camera realism
- handheld phone-camera perspective
- casual creator content
- candid private moments
- imperfect framing
- slight camera tilt
- natural body positioning
- realistic apartment lighting
- lamp lighting
- bedside lighting
- couch lighting
- evening ambient lighting
- lived-in environments
- authentic creator energy
- "sent this just for you" feeling

The viewer should feel:

"she took this for me"

NOT:

"a professional photographer took this"

Avoid:

- luxury boudoir photography
- magazine photography
- studio lighting
- professional glamour photography
- perfect commercial composition
- perfect editorial posing
- luxury hotel marketing photography
- real-estate photography energy
- overly polished luxury interiors
- fashion campaign styling

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

SCENE DIVERSITY RULE:

The user's tags define REQUIRED ELEMENTS.

The user's tags do NOT define a single scene.

Extract:

- wardrobe requirements
- nudity requirements
- location requirements
- atmosphere requirements

Then generate completely different visual scenarios.

Example:

fireplace, crop top, booty shorts

Required elements:

- fireplace
- crop top
- booty shorts

DO NOT repeat the same fireplace scene.

Create different interactions around the fireplace.

Example concepts:

- sitting on hearth
- lying on rug
- sitting in chair beside fireplace
- leaning on mantel
- curled up on couch
- standing in doorway
- sitting on floor
- stretching beside fireplace
- window seat near fireplace
- reading beside fireplace

The required elements remain.

The scene must change.

LOCATION DIVERSITY RULE:

Every prompt must use a different primary setting or micro-location.

Do NOT keep every prompt in the same exact place.

If the user gives one broad location, expand it into related nearby locations.

Examples:

hotel lounge:
- velvet chaise in hotel lounge
- private hotel suite
- window seat overlooking city lights
- hotel balcony doorway
- upscale cocktail bar corner
- marble bathroom mirror
- hotel bedroom couch
- penthouse sitting area
- hallway doorway
- terrace seating

indoors:
- couch
- bedroom
- kitchen island
- bathroom mirror
- hallway doorway
- window seat
- fireplace rug
- balcony doorway
- bed edge
- apartment floor

outdoors:
- porch
- dock
- field
- garden path
- cabin steps
- lakeside rocks
- fence line
- balcony
- trail overlook
- backyard chair

pool:
- pool edge
- submerged steps
- cabana
- poolside daybed
- outdoor shower
- hot tub
- balcony overlooking pool
- pool bar
- lounge chair
- private courtyard

Generate multiple unique interactions with the broad theme.

Do not repeatedly place the subject in the same spot.

Every prompt must involve a different:

- interaction point
- activity
- furniture element
- architectural element
- perspective
- storytelling moment

Changing only pose does not count.

Changing only expression does not count.

Changing only camera angle does not count.

Each prompt should feel like a different day and a different moment.

CRITICAL RULE:

No primary scene concept may be reused.

If one prompt uses:

- fireplace hearth

another prompt may not use:

- fireplace hearth

If one prompt uses:

- couch beside fireplace

another prompt may not use:

- couch beside fireplace

Each prompt must begin from a different visual concept.

PROMPT REQUIREMENTS:
COMPOSITION DIVERSITY:

Intentionally vary composition across the batch.

Include a mix of:

- chest-up portraits
- waist-up portraits
- upper-thigh framing
- seated full-body compositions
- reclining compositions
- leaning compositions
- kneeling compositions
- over-the-shoulder perspectives
- side-profile perspectives
- three-quarter body angles
- low-angle perspectives
- eye-level perspectives
- slightly elevated perspectives

Do not default to:
- seated smiling at camera
- leaning toward camera
- direct eye contact in every prompt

Some prompts should feel:
- playful
- teasing
- happy
- excited
- bright
- warm
- flirtatious
- relaxed
- dreamy
- mischievous
- candid
- contemplative
- caught-in-the-moment

Not every prompt should use:
- soft smile
- direct eye contact
- inviting gaze

FACIAL EXPRESSION AND PERSONALITY REQUIREMENT:

Give her visible personality and life in every prompt.

Most prompts should make her look warm, playful, quietly happy, confident,
flirty, amused, or genuinely engaged.
Expressions must look candid and believable, not forced, fake, exaggerated,
plastic, or overacted.
Favor subtle eye warmth, relaxed cheeks, small asymmetry, natural mouth shape,
and in-the-moment micro-expressions over big posed smiles.

Use a varied expression palette such as:

- soft genuine smile that reaches her eyes
- subtle playful smile
- candid amused half-smile
- warm relaxed expression
- teasing eye contact
- relaxed mischievous smirk
- coy over-the-shoulder half-smile
- flirty slight parted-lip smile
- confident inviting gaze
- candid laugh caught mid-moment
- playful raised eyebrow
- soft seductive smile
- relaxed happy glow

Avoid:
- blank expression
- neutral face
- bored face
- monotone expression
- mannequin-like face
- lifeless stare
- forced smile
- fake grin
- overly toothy smile
- frozen pageant smile
- uncanny perfect smile
- exaggerated open-mouth acting
- dead eyes with a pasted-on smile
- the same calm smile in every prompt

Vary emotional presentation naturally.
Do not repeat the same facial gesture across the batch.

- Return exactly {prompt_count} prompts
- Number the prompts
- Each prompt must be substantially different
- Every prompt must explicitly include: full natural D-cup bust
- Every prompt must explicitly include: feminine hourglass body
- Every prompt must explicitly include: same waist-to-hip proportions
- Every prompt must explicitly include: rich dark tan skin
- Every prompt must visibly preserve the same body size, bust size, and recognizable body structure from the reference image
- Every prompt must include concrete wardrobe or lingerie detail unless nudity was explicitly requested by the user
- Every prompt must use close-up, close-medium, waist-up, upper-thigh, or head-to-thigh creator framing by default, unless the user specifically asks for a different framing style in the Optional Setting / Direction field or creative tags
- Every prompt must keep her body large in frame and avoid distant scenery-dominant composition
- Every prompt must include pose, body orientation, camera angle, close shot distance, crop, lighting, expression, and environment detail
- Every prompt must include a clearly described natural facial expression with warm, playful, quietly happy, confident, teasing, flirty, or genuinely engaged energy
- Most prompts should make her feel alive and personable, not calm, blank, bored, monotone, expressionless, fake-smiling, or overacted
- Every prompt must include realistic texture detail such as skin, hair, fabric, shadows, reflections, bedding, furniture, window light, or room surfaces where appropriate
- Every prompt must be detailed enough to generate a complete premium creator image without needing assumptions
- Every prompt must feel close, intimate, realistic, and premium, not vague or generic
- Every prompt must remain teaser/premium-safe unless the user explicitly requests nude, topless, naked, or bare breasts
- Do not include graphic sexual acts or graphic genital detail in Premium Prompts
- Every prompt must begin from a different visual concept
- Every prompt must use a different primary setting or micro-location
- Do not reuse the same room, furniture piece, corner, seating position, or environmental interaction twice
- If the user provides a broad location theme, expand into related nearby settings
- Use different shot types throughout the batch
- Use different camera angles throughout the batch
- Use different environments throughout the batch
- Use different poses throughout the batch
- Use different body orientations throughout the batch
- Use different furniture interactions throughout the batch
- Use different storytelling moments throughout the batch
- Use different emotional energy throughout the batch
- Use different facial expressions throughout the batch
- Use different viewer-connection styles throughout the batch
- Mix direct eye contact, over-the-shoulder glances, playful looks, soft smiles, teasing expressions, candid moments, and relaxed expressions
- Preserve the same woman in every image
- Write complete WAN 2.7 image-edit prompts
- Each prompt should feel close, personal, realistic, and creator-captured
- Each prompt should prioritize the woman over the scenery
- Each prompt should include an expression or viewer-connection detail
- Each prompt should include body language or a natural micro-behavior
- Each prompt should include camera distance or framing
- Each prompt should include lighting
- Vary sentence structure throughout the batch
- Do not begin prompts with the same phrase repeatedly
- Prompt openings should vary naturally throughout the batch
- Writing style should vary naturally across prompts
- Avoid template-like repetition
- Lighting descriptions should vary substantially across prompts
- Avoid repeating identical lighting language throughout the batch

Examples of acceptable variation:

hotel lounge:
- chaise lounge
- leather chair
- sectional sofa
- cocktail table
- window seat
- balcony doorway
- penthouse sitting area
- hotel suite couch
- marble bathroom mirror
- terrace seating

indoors:
- couch
- bed edge
- kitchen island
- fireplace chair
- window ledge
- hallway doorway
- bathroom mirror
- balcony doorway
- reading chair
- floor cushion

outdoors:
- garden path
- porch swing
- lakeside rocks
- dock edge
- cabin steps
- fence line
- trail overlook
- backyard chair
- tree stump
- field grass

Changing only:
- expression
- smile
- hand placement
- eye direction

does NOT count as scene variety.

Each prompt should feel like it was captured on a different day in a different moment while preserving the user's required tags.

If the user requests topless:

EVERY prompt must clearly depict:

- topless presentation
- visible bare breasts
- naturally visible nipples
- no bra
- no shirt
- no crop top
- no upper-body clothing

Toplessness must remain obvious in every image.

However:

- Vary the wording naturally throughout the batch
- Do not begin every prompt with the same topless phrase
- Do not repeat identical topless wording in every prompt
- Integrate toplessness naturally into the scene description
- Some prompts may mention toplessness near the beginning
- Some prompts may mention toplessness in the pose description
- Some prompts may mention toplessness in the body-language description

Examples of acceptable variation:

- topless with bare breasts visible
- bare-chested with natural breasts visible
- topless presentation with visible natural nipples
- upper body uncovered with bare breasts visible
- relaxed topless pose with natural breast visibility

The topless state must remain unmistakable, but the wording should not become repetitive.


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
- If topless, bare breasts, nude, naked, or completely nude content is requested, preserve the reference image's full natural D-cup bust size in every prompt
- Maintain full breast projection
- Maintain rounded natural breast contours
- Do not reduce bust volume
- Do not reinterpret the chest as smaller than the reference image
- If topless, bare breasts, or nude content is requested, do not reduce breast volume or make the breasts appear smaller than the reference image
- If topless, bare breasts, or nude content is requested, include natural rounded breast shape, visible breast projection, and perky nipples when visible

- If nudity is requested, do not alternate between clothed and unclothed prompts

- If nude, nudity, naked, topless, or bare breasts are requested, do not include clothing or outfit alternatives unless explicitly requested by the user

- Do not include explanations
- Do not include introductions
- Do not include summaries
- Output prompts only
"""
