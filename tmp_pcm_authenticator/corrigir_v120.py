from pathlib import Path
p = Path('build_src/PCM_Authenticator/app/src/main/java/br/com/pcm/authenticator/MainActivity.java')
t = p.read_text(encoding='utf-8')
for icone, rotulo in [('●','Instalações'),('◷','Histórico'),('⚙','Configurações'),('ⓘ','Sobre')]:
    t = t.replace(f'itemNav("{icone}\n{rotulo}"', f'itemNav("{icone}\\n{rotulo}"')
p.write_text(t, encoding='utf-8')
print('Escapes da navegação corrigidos')