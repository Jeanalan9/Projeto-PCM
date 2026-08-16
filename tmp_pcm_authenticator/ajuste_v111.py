from pathlib import Path

caminho = Path('build_src/PCM_Authenticator/app/src/main/java/br/com/pcm/authenticator/MainActivity.java')
texto = caminho.read_text(encoding='utf-8')

# 1) Campo de renovacao passa a ser somente selecao por calendario.
antigo = '''EditText nome=campo("Ex.: Sorel - Matriz"), id=campo("Ex.: PCM-8F21-74AD"), segredo=campo("Chave Base32"), renovacao=campo("DD/MM/AAAA"); segredo.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD); renovacao.setInputType(InputType.TYPE_CLASS_DATETIME|InputType.TYPE_DATETIME_VARIATION_DATE); addCampo(box,"Nome da empresa / instalação",nome); addCampo(box,"Identificador",id); addCampo(box,"Segredo Base32",segredo); addCampo(box,"Próxima renovação",renovacao);'''
novo = '''EditText nome=campo("Ex.: Sorel - Matriz"), id=campo("Ex.: PCM-8F21-74AD"), segredo=campo("Chave Base32"), renovacao=campo("Selecionar data"); segredo.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD); renovacao.setInputType(InputType.TYPE_NULL); renovacao.setFocusable(false); renovacao.setFocusableInTouchMode(false); renovacao.setCursorVisible(false); renovacao.setClickable(true); renovacao.setCompoundDrawablesWithIntrinsicBounds(0,0,android.R.drawable.ic_menu_my_calendar,0); renovacao.setCompoundDrawablePadding(dp(10)); renovacao.setOnClickListener(v->{ Calendar base=Calendar.getInstance(); String atual=renovacao.getText().toString().trim(); if(!atual.isEmpty()){ try{ SimpleDateFormat f=new SimpleDateFormat("dd/MM/yyyy",Locale.getDefault()); f.setLenient(false); base.setTime(f.parse(atual)); }catch(Exception ignored){} } DatePickerDialog seletor=new DatePickerDialog(this,(view,ano,mes,dia)->renovacao.setText(String.format(Locale.getDefault(),"%02d/%02d/%04d",dia,mes+1,ano)),base.get(Calendar.YEAR),base.get(Calendar.MONTH),base.get(Calendar.DAY_OF_MONTH)); seletor.setTitle("Próxima renovação"); seletor.show(); }); addCampo(box,"Nome da empresa / instalação",nome); addCampo(box,"Identificador",id); addCampo(box,"Segredo Base32",segredo); addCampo(box,"Próxima renovação",renovacao);'''
if antigo not in texto:
    raise SystemExit('Trecho do campo de renovacao nao encontrado')
texto = texto.replace(antigo, novo)

# 2) Mais respiro e sombra real nos botoes do card.
antigo = '''LinearLayout acoes=new LinearLayout(this); LinearLayout.LayoutParams al=new LinearLayout.LayoutParams(-1,-2); al.topMargin=dp(14); final String cf=codigo; Button copiar=botao("Copiar código",VERDE); copiar.setOnClickListener(v->copiar(cf)); acoes.addView(copiar,new LinearLayout.LayoutParams(0,dp(46),1)); Button remover=botao("Remover",ERRO); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(46),1); rp.leftMargin=dp(9); final int pos=idx; remover.setOnClickListener(v->excluir(pos)); acoes.addView(remover,rp); c.addView(acoes,al);'''
novo = '''LinearLayout acoes=new LinearLayout(this); acoes.setClipChildren(false); acoes.setClipToPadding(false); acoes.setPadding(dp(2),dp(4),dp(2),dp(7)); LinearLayout.LayoutParams al=new LinearLayout.LayoutParams(-1,-2); al.topMargin=dp(12); al.bottomMargin=dp(2); final String cf=codigo; Button copiar=botao("Copiar código",VERDE); copiar.setElevation(dp(3)); copiar.setOnClickListener(v->copiar(cf)); LinearLayout.LayoutParams cpb=new LinearLayout.LayoutParams(0,dp(48),1); cpb.leftMargin=dp(1); cpb.rightMargin=dp(5); acoes.addView(copiar,cpb); Button remover=botao("Remover",ERRO); remover.setElevation(dp(3)); LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(48),1); rp.leftMargin=dp(5); rp.rightMargin=dp(1); final int pos=idx; remover.setOnClickListener(v->excluir(pos)); acoes.addView(remover,rp); c.addView(acoes,al);'''
if antigo not in texto:
    raise SystemExit('Trecho dos botoes do card nao encontrado')
texto = texto.replace(antigo, novo)

# 3) Botoes do formulario tambem recebem area de sombra e espacamento.
antigo = '''LinearLayout acoes=new LinearLayout(this); Button cancelar=botao("Cancelar",SEC); cancelar.setOnClickListener(v->d.dismiss()); acoes.addView(cancelar,new LinearLayout.LayoutParams(0,dp(50),1)); Button salvar=new Button(this); salvar.setText("Salvar instalação"); salvar.setAllCaps(false); salvar.setTextColor(Color.WHITE); salvar.setTypeface(Typeface.DEFAULT,Typeface.BOLD); salvar.setBackground(bg(VERDE,12)); LinearLayout.LayoutParams sl=new LinearLayout.LayoutParams(0,dp(50),1); sl.leftMargin=dp(10); acoes.addView(salvar,sl); LinearLayout.LayoutParams alp=new LinearLayout.LayoutParams(-1,-2); alp.topMargin=dp(20); box.addView(acoes,alp);'''
novo = '''LinearLayout acoes=new LinearLayout(this); acoes.setClipChildren(false); acoes.setClipToPadding(false); acoes.setPadding(dp(2),dp(4),dp(2),dp(7)); Button cancelar=botao("Cancelar",SEC); cancelar.setElevation(dp(3)); cancelar.setOnClickListener(v->d.dismiss()); LinearLayout.LayoutParams clp=new LinearLayout.LayoutParams(0,dp(50),1); clp.rightMargin=dp(5); acoes.addView(cancelar,clp); Button salvar=new Button(this); salvar.setText("Salvar instalação"); salvar.setAllCaps(false); salvar.setTextColor(Color.WHITE); salvar.setTypeface(Typeface.DEFAULT,Typeface.BOLD); salvar.setBackground(bg(VERDE,12)); salvar.setElevation(dp(3)); LinearLayout.LayoutParams sl=new LinearLayout.LayoutParams(0,dp(50),1); sl.leftMargin=dp(5); acoes.addView(salvar,sl); LinearLayout.LayoutParams alp=new LinearLayout.LayoutParams(-1,-2); alp.topMargin=dp(17); alp.bottomMargin=dp(2); box.addView(acoes,alp);'''
if antigo not in texto:
    raise SystemExit('Trecho dos botoes do formulario nao encontrado')
texto = texto.replace(antigo, novo)

# 4) Botao principal ganha elevacao e folga para a sombra.
antigo = '''add.setBackground(bg(VERDE,14)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54)); ap.topMargin=dp(6); conteudo.addView(add,ap);'''
novo = '''add.setBackground(bg(VERDE,14)); add.setElevation(dp(3)); add.setOnClickListener(v->cadastro()); LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54)); ap.topMargin=dp(8); ap.bottomMargin=dp(4); conteudo.addView(add,ap);'''
if antigo not in texto:
    raise SystemExit('Trecho do botao principal nao encontrado')
texto = texto.replace(antigo, novo)

caminho.write_text(texto, encoding='utf-8')
print('Ajustes v1.1.1 aplicados com sucesso')
