{/*
  LogoCarousel component for the Agent Skills documentation.
  Shows logos in two scrolling rows for fair exposure.

  To add a new logo:
  1. Add logo files to /images/logos/[logo-name]/
  2. Add entry to the logos array below
*/}

export const LogoCarousel = () => {
  // Fixed order - no shuffling to avoid SSR hydration mismatch
  const logos = [
    { name: "Gemini CLI", url: "https://geminicli.com", lightSrc: "/assets/images/logos/gemini-cli/gemini-cli-logo_light.svg", darkSrc: "/assets/images/logos/gemini-cli/gemini-cli-logo_dark.svg" },
    { name: "Autohand Code CLI", url: "https://autohand.ai/", lightSrc: "/assets/images/logos/autohand/autohand-light.svg", darkSrc: "/assets/images/logos/autohand/autohand-dark.svg", width: "120px" },
    { name: "OpenCode", url: "https://opencode.ai/", lightSrc: "/assets/images/logos/opencode/opencode-wordmark-light.svg", darkSrc: "/assets/images/logos/opencode/opencode-wordmark-dark.svg" },
    { name: "Mux", url: "https://mux.coder.com/", lightSrc: "/assets/images/logos/mux/mux-editor-light.svg", darkSrc: "/assets/images/logos/mux/mux-editor-dark.svg", width: "120px" },
    { name: "Cursor", url: "https://cursor.com/", lightSrc: "/assets/images/logos/cursor/LOCKUP_HORIZONTAL_2D_LIGHT.svg", darkSrc: "/assets/images/logos/cursor/LOCKUP_HORIZONTAL_2D_DARK.svg" },
    { name: "Amp", url: "https://ampcode.com/", lightSrc: "/assets/images/logos/amp/amp-logo-light.svg", darkSrc: "/assets/images/logos/amp/amp-logo-dark.svg", width: "120px" },
    { name: "Letta", url: "https://www.letta.com/", lightSrc: "/assets/images/logos/letta/Letta-logo-RGB_OffBlackonTransparent.svg", darkSrc: "/assets/images/logos/letta/Letta-logo-RGB_GreyonTransparent.svg" },
    { name: "Firebender", url: "https://firebender.com/", lightSrc: "/assets/images/logos/firebender/firebender-wordmark-light.svg", darkSrc: "/assets/images/logos/firebender/firebender-wordmark-dark.svg" },
    { name: "Goose", url: "https://block.github.io/goose/", lightSrc: "/assets/images/logos/goose/goose-logo-black.png", darkSrc: "/assets/images/logos/goose/goose-logo-white.png" },
    { name: "GitHub", url: "https://github.com/", lightSrc: "/assets/images/logos/github/GitHub_Lockup_Dark.svg", darkSrc: "/assets/images/logos/github/GitHub_Lockup_Light.svg" },
    { name: "VS Code", url: "https://code.visualstudio.com/", lightSrc: "/assets/images/logos/vscode/vscode.svg", darkSrc: "/assets/images/logos/vscode/vscode-alt.svg" },
    { name: "Claude Code", url: "https://claude.ai/code", lightSrc: "/assets/images/logos/claude-code/Claude-Code-logo-Slate.svg", darkSrc: "/assets/images/logos/claude-code/Claude-Code-logo-Ivory.svg" },
    { name: "Claude", url: "https://claude.ai/", lightSrc: "/assets/images/logos/claude-ai/Claude-logo-Slate.svg", darkSrc: "/assets/images/logos/claude-ai/Claude-logo-Ivory.svg" },
    { name: "OpenAI Codex", url: "https://developers.openai.com/codex", lightSrc: "/assets/images/logos/oai-codex/OAI_Codex-Lockup_400px.svg", darkSrc: "/assets/images/logos/oai-codex/OAI_Codex-Lockup_400px_Darkmode.svg" },
    { name: "Piebald", url: "https://piebald.ai", lightSrc: "/assets/images/logos/piebald/Piebald_wordmark_light.svg", darkSrc: "/assets/images/logos/piebald/Piebald_wordmark_dark.svg" },
    { name: "Factory", url: "https://factory.ai/", lightSrc: "/assets/images/logos/factory/factory-logo-light.svg", darkSrc: "/assets/images/logos/factory/factory-logo-dark.svg" },
    { name: "pi", url: "https://shittycodingagent.ai/", lightSrc: "/assets/images/logos/pi/pi-logo-light.svg", darkSrc: "/assets/images/logos/pi/pi-logo-dark.svg", width: "80px" },
    { name: "Databricks", url: "https://databricks.com/", lightSrc: "/assets/images/logos/databricks/databricks-logo-light.svg", darkSrc: "/assets/images/logos/databricks/databricks-logo-dark.svg" },
    { name: "Agentman", url: "https://agentman.ai/", lightSrc: "/assets/images/logos/agentman/agentman-wordmark-light.svg", darkSrc: "/assets/images/logos/agentman/agentman-wordmark-dark.svg" },
    { name: "TRAE", url: "https://trae.ai/", lightSrc: "/assets/images/logos/trae/trae-logo-lightmode.svg", darkSrc: "/assets/images/logos/trae/trae-logo-darkmode.svg" },
    { name: "Spring AI", url: "https://docs.spring.io/spring-ai/reference", lightSrc: "/assets/images/logos/spring-ai/spring-ai-logo-light.svg", darkSrc: "/assets/images/logos/spring-ai/spring-ai-logo-dark.svg" },
    { name: "Roo Code", url: "https://roocode.com", lightSrc: "/assets/images/logos/roo-code/roo-code-logo-black.svg", darkSrc: "/assets/images/logos/roo-code/roo-code-logo-white.svg" },
    { name: "Mistral AI Vibe", url: "https://github.com/mistralai/mistral-vibe", lightSrc: "/assets/images/logos/mistral-vibe/vibe-logo_black.svg", darkSrc: "/assets/images/logos/mistral-vibe/vibe-logo_white.svg", width: "80px" },
    { name: "Command Code", url: "https://commandcode.ai/", lightSrc: "/assets/images/logos/command-code/command-code-logo-for-light.svg", darkSrc: "/assets/images/logos/command-code/command-code-logo-for-dark.svg", width: "200px" },
    { name: "Ona", url: "https://ona.com", lightSrc: "/assets/images/logos/ona/ona-wordmark-light.svg", darkSrc: "/assets/images/logos/ona/ona-wordmark-dark.svg", width: "120px" },
    { name: "VT Code", url: "https://github.com/vinhnx/vtcode", lightSrc: "/assets/images/logos/vtcode/vt_code_light.svg", darkSrc: "/assets/images/logos/vtcode/vt_code_dark.svg" },
    { name: "Qodo", url: "https://www.qodo.ai/", lightSrc: "/assets/images/logos/qodo/qodo-logo-light.png", darkSrc: "/assets/images/logos/qodo/qodo-logo-dark.svg" },
    { name: "Live Log Insight", url: "#", lightSrc: "/assets/images/add_ins/logo/logo.png", darkSrc: "/assets/images/add_ins/logo/logo.png", width: "120px" },
  ];

  // Split into two rows - fixed order, no shuffling
  const row1 = logos.filter((_, i) => i % 2 === 0);
  const row2 = logos.filter((_, i) => i % 2 === 1);
  const row1Doubled = [...row1, ...row1];
  const row2Doubled = [...row2, ...row2];

  return (
    <>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 50s linear infinite' }}>
          {row1Doubled.map((logo, i) => (
            <a key={`${logo.name}-${i}`} href={logo.url} style={{ textDecoration: 'none', border: 'none' }}>
              <img className="block dark:hidden object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.lightSrc} alt={logo.name} />
              <img className="hidden dark:block object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.darkSrc} alt={logo.name} />
            </a>
          ))}
        </div>
      </div>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 60s linear infinite reverse' }}>
          {row2Doubled.map((logo, i) => (
            <a key={`${logo.name}-${i}`} href={logo.url} style={{ textDecoration: 'none', border: 'none' }}>
              <img className="block dark:hidden object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.lightSrc} alt={logo.name} />
              <img className="hidden dark:block object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.darkSrc} alt={logo.name} />
            </a>
          ))}
        </div>
      </div>
    </>
  );
};
