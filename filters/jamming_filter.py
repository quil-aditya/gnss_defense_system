# filters/jamming_filter.py

def jamming_filter(jamInd, noise_per_ms):
    """
    Apply hardcoded thresholds to detect definitely jammed/spoofed signals.

    Parameters:
        jamInd (float): Jamming Indicator (0–15)
        noise_per_ms (float): Receiver noise level (0–4.0+)

    Returns:
        str: 'reject' → signal is rejected immediately
             'ai_zone' → pass to AI for further decision
             'safe' → signal passes to FC directly (used elsewhere)
    """

    if jamInd >= 10 or noise_per_ms >= 3.0:
        return 'reject'

    elif 8 <= jamInd < 10 or 2.8 <= noise_per_ms < 3.0:
        return 'ai_zone'

    else:
        return 'bypass_candidate'
