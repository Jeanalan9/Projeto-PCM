from pathlib import Path

caminho = Path('build_src/PCM_Authenticator/app/src/main/java/br/com/pcm/authenticator/MainActivity.java')
texto = caminho.read_text(encoding='utf-8')

# Aproxima todo o conteúdo da área segura inferior real do Android.
antigo = 'conteudo.setPadding(dp(20),top+dp(12),dp(20),bottom+dp(16));'
novo = 'conteudo.setPadding(dp(20),top+dp(12),dp(20),bottom+dp(4));'
if antigo not in texto:
    raise SystemExit('Padding inferior principal não encontrado')
texto = texto.replace(antigo, novo)

# Barra inferior maior, mais legível e posicionada imediatamente acima da área segura do Android.
antigo = '''        LinearLayout nav=new LinearLayout(this); nav.setGravity(Gravity.CENTER); nav.setPadding(0,dp(7),0,dp(1));
        nav.addView(itemNav("●\\nInstalações",true),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("◷\\nHistórico",false),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("⚙\\nConfigurações",false),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("ⓘ\\nSobre",false),new LinearLayout.LayoutParams(0,dp(48),1));
        conteudo.addView(nav,new LinearLayout.LayoutParams(-1,dp(56)));'''
novo = '''        LinearLayout nav=new LinearLayout(this); nav.setGravity(Gravity.CENTER); nav.setPadding(0,dp(5),0,0);
        nav.addView(itemNav("●\\nInstalações",true),new LinearLayout.LayoutParams(0,dp(60),1));
        nav.addView(itemNav("◷\\nHistórico",false),new LinearLayout.LayoutParams(0,dp(60),1));
        nav.addView(itemNav("⚙\\nConfigurações",false),new LinearLayout.LayoutParams(0,dp(60),1));
        nav.addView(itemNav("ⓘ\\nSobre",false),new LinearLayout.LayoutParams(0,dp(60),1));
        conteudo.addView(nav,new LinearLayout.LayoutParams(-1,dp(64)));'''
if antigo not in texto:
    raise SystemExit('Estrutura da barra inferior v1.2.0 não encontrada')
texto = texto.replace(antigo, novo)

antigo = 'TextView t=txt(textoNav,9,ativo?TEXTO:SEC,ativo); t.setGravity(Gravity.CENTER); t.setLineSpacing(0,.9f);'
novo = 'TextView t=txt(textoNav,11,ativo?TEXTO:SEC,ativo); t.setGravity(Gravity.CENTER); t.setLineSpacing(dp(2),1.0f);'
if antigo not in texto:
    raise SystemExit('Tipografia dos itens da barra inferior não encontrada')
texto = texto.replace(antigo, novo)

caminho.write_text(texto, encoding='utf-8')
print('Barra inferior PCM Authenticator v1.2.1 ajustada com sucesso')
