def show_dry_run_preview(
    generation_mode,
    platform_mode,
    spice_level,
    user_request,
    prompts,
):
    print("\n" + "=" * 80)
    print("🔥 DRY RUN MODE ENABLED")
    print("=" * 80)

    print(f"Generation Mode : {generation_mode['name']}")
    print(f"Platform Mode   : {platform_mode}")
    print(f"Spice Level     : {spice_level}")

    print("\nUSER TAGS:")
    print(user_request)

    print("\n" + "=" * 80)
    print("GENERATED PROMPT PREVIEW")
    print("=" * 80)

    for i, prompt in enumerate(prompts, start=1):
        print(f"\n[{i}]")
        print(prompt)

    print("\n" + "=" * 80)
    print("✅ No WaveSpeed credits used.")
    print("✅ No image generation performed.")
    print("✅ Prompt orchestration preview only.")
    print("=" * 80 + "\n")