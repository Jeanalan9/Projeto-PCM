from pathlib import Path

caminho = Path('build_src/PCM_Authenticator/app/src/main/java/br/com/pcm/authenticator/MainActivity.java')
texto = caminho.read_text(encoding='utf-8')

# Paleta PCM: branco/preto/cinza, vermelho apenas destrutivo e amarelo suave para alerta.
antigo = 'private static final int FUNDO=Color.rgb(249,249,246), CARD=Color.WHITE, VERDE=Color.rgb(20,92,55), VERDE2=Color.rgb(93,157,70), TEXTO=Color.rgb(27,36,31), SEC=Color.rgb(101,111,105), BORDA=Color.rgb(226,230,224), SUAVE=Color.rgb(241,245,239), ALERTA=Color.rgb(183,122,35), ERRO=Color.rgb(177,61,61);'
novo = 'private static final int FUNDO=Color.rgb(250,250,250), CARD=Color.WHITE, VERDE=Color.rgb(17,17,17), VERDE2=Color.rgb(17,17,17), TEXTO=Color.rgb(17,17,17), SEC=Color.rgb(102,102,102), BORDA=Color.rgb(226,226,226), SUAVE=Color.rgb(244,244,244), ALERTA=Color.rgb(154,98,0), ERRO=Color.rgb(229,57,53);'
if antigo not in texto: raise SystemExit('Paleta base nao encontrada')
texto = texto.replace(antigo, novo)

# Cabecalho compacto no padrao PCM.
inicio = texto.index('    private void cabecalho(){')
fim = texto.index('    private void renderizar(){', inicio)
novo_cab = '''    private void cabecalho(){
        LinearLayout linha=new LinearLayout(this); linha.setGravity(Gravity.CENTER_VERTICAL);
        TextView logo=txt("⚙",25,TEXTO,true); logo.setGravity(Gravity.CENTER); linha.addView(logo,new LinearLayout.LayoutParams(dp(36),dp(42)));
        LinearLayout tituloLinha=new LinearLayout(this); tituloLinha.setGravity(Gravity.CENTER_VERTICAL); LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,-2,1); tp.leftMargin=dp(6); linha.addView(tituloLinha,tp);
        tituloLinha.addView(txt("PCM",20,TEXTO,true)); TextView nome=txt("Authenticator",13,TEXTO,true); LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(-2,-2); np.leftMargin=dp(6); tituloLinha.addView(nome,np);
        contador=txt("",11,TEXTO,true); contador.setGravity(Gravity.CENTER); contador.setPadding(dp(10),dp(8),dp(10),dp(8)); contador.setBackground(borda(Color.WHITE,20,BORDA)); linha.addView(contador);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.bottomMargin=dp(18); conteudo.addView(linha,lp);
    }

    private void navegacaoInferior(){
        View div=new View(this); div.setBackgroundColor(BORDA); conteudo.addView(div,new LinearLayout.LayoutParams(-1,dp(1)));
        LinearLayout nav=new LinearLayout(this); nav.setGravity(Gravity.CENTER); nav.setPadding(0,dp(7),0,dp(1));
        nav.addView(itemNav("●\nInstalações",true),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("◷\nHistórico",false),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("⚙\nConfigurações",false),new LinearLayout.LayoutParams(0,dp(48),1));
        nav.addView(itemNav("ⓘ\nSobre",false),new LinearLayout.LayoutParams(0,dp(48),1));
        conteudo.addView(nav,new LinearLayout.LayoutParams(-1,dp(56)));
    }

    private TextView itemNav(String textoNav,boolean ativo){
        TextView t=txt(textoNav,9,ativo?TEXTO:SEC,ativo); t.setGravity(Gravity.CENTER); t.setLineSpacing(0,.9f);
        if(!ativo)t.setOnClickListener(v->Toast.makeText(this,"Funcionalidade prevista para uma próxima versão",Toast.LENGTH_SHORT).show());
        return t;
    }

'''
texto = texto[:inicio] + novo_cab + texto[fim:]

# Inserir navegacao inferior abaixo do botao principal.
antigo = 'add.setBackground(bg(VERDE,14)); add.setElevation(dp(3)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54)); ap.topMargin=dp(8); ap.bottomMargin=dp(4); conteudo.addView(add,ap);\n        setContentView(raiz); renderizar(); raiz.requestApplyInsets();'
novo = 'add.setBackground(bg(VERDE,12)); add.setElevation(dp(2)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(52)); ap.topMargin=dp(8); ap.bottomMargin=dp(8); conteudo.addView(add,ap);\n        navegacaoInferior();\n        setContentView(raiz); renderizar(); raiz.requestApplyInsets();'
if antigo not in texto: raise SystemExit('Botao principal v111 nao encontrado')
texto = texto.replace(antigo, novo)

# Card: tons neutros e botoes com contorno PCM.
texto = texto.replace('cs==ERRO?Color.rgb(250,239,239):cs==ALERTA?Color.rgb(250,244,232):Color.rgb(237,246,239)', 'cs==ERRO?Color.rgb(255,242,242):cs==ALERTA?Color.rgb(255,241,214):Color.rgb(245,245,245)')
texto = texto.replace('TextView r=txt("Próxima renovação  •  "+ins.renovacao,12,VERDE,false);', 'TextView r=txt("Próxima renovação  •  "+ins.renovacao,12,TEXTO,false);')

# Copiar com preto; remover com vermelho e contorno apropriado.
antigo = 'Button copiar=botao("Copiar código",VERDE); copiar.setElevation(dp(3)); copiar.setOnClickListener(v->copiar(cf));'
novo = 'Button copiar=botao("Copiar código",TEXTO); copiar.setBackground(borda(CARD,12,Color.rgb(160,160,160))); copiar.setElevation(dp(2)); copiar.setOnClickListener(v->copiar(cf));'
if antigo in texto: texto = texto.replace(antigo, novo)
antigo = 'Button remover=botao("Remover",ERRO); remover.setElevation(dp(3));'
novo = 'Button remover=botao("Remover",ERRO); remover.setBackground(borda(CARD,12,ERRO)); remover.setElevation(dp(2));'
if antigo in texto: texto = texto.replace(antigo, novo)

# Formulario: bloco de ajuda cinza e botoes mais PCM.
texto = texto.replace('TextView ajuda=txt("O segredo será cifrado e protegido no próprio aparelho.",11,SEC,false);', 'TextView ajuda=txt("ⓘ   O segredo será cifrado e protegido no próprio aparelho.",11,TEXTO,false); ajuda.setPadding(dp(12),dp(10),dp(12),dp(10)); ajuda.setBackground(bg(SUAVE,10));')
texto = texto.replace('Button cancelar=botao("Cancelar",SEC);', 'Button cancelar=botao("Cancelar",TEXTO); cancelar.setBackground(borda(CARD,12,Color.rgb(160,160,160)));')

# Confirmacao destrutiva: cancelar preto, remover vermelho.
texto = texto.replace('d.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(VERDE);', 'd.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(TEXTO);')

caminho.write_text(texto, encoding='utf-8')
print('Tema visual PCM v1.2.0 aplicado com sucesso')
