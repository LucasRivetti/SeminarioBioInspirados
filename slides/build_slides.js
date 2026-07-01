const pptxgen = require("pptxgenjs");
const FIG = "/tmp/proj/resultados/figuras/";
const p = new pptxgen();
p.layout = "LAYOUT_16x9";
p.author = "Lucas Rivetti e Ian Nunes";
p.title = "VMPACS - Alocacao de VMs";
const DARK="15323B", INK="1F2933", MUTED="6B7280", TEAL="0E7C86",
      RED="C0392B", SLATE="2C3E50", LIGHT="EEF3F4", WHITE="FFFFFF";
const FH="Cambria", FB="Calibri";
const shadow = () => ({type:"outer", color:"000000", blur:7, offset:3, angle:90, opacity:0.10});
function header(s, num, titulo){
  s.addShape(p.shapes.OVAL,{x:0.5,y:0.36,w:0.55,h:0.55,fill:{color:TEAL}});
  s.addText(num,{x:0.5,y:0.36,w:0.55,h:0.55,align:"center",valign:"middle",fontFace:FH,fontSize:20,bold:true,color:WHITE,margin:0});
  s.addText(titulo,{x:1.2,y:0.34,w:8.4,h:0.6,align:"left",valign:"middle",fontFace:FH,fontSize:26,bold:true,color:DARK,margin:0});
}
function card(s,x,y,w,h,fill){ s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.08,fill:{color:fill||WHITE},shadow:shadow()}); }
function bullets(s,items,x,y,w,h,fs){
  s.addText(items.map((t)=>({text:t,options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:7,color:INK,fontSize:fs||14}})),
    {x,y,w,h,fontFace:FB,valign:"top",margin:2});
}
function rodape(s,num,dark){ s.addText(String(num),{x:9.0,y:5.26,w:0.72,h:0.3,align:"right",fontFace:FB,fontSize:11,color:dark?"7E97A0":"9AA5AD",margin:0}); }

// 1 TITULO
let s=p.addSlide(); s.background={color:DARK};
const nodes=[[8.4,1.0],[9.1,1.7],[8.2,2.3],[9.3,3.1],[8.6,3.8]];
for(let i=0;i<nodes.length-1;i++) s.addShape(p.shapes.LINE,{x:nodes[i][0]+0.12,y:nodes[i][1]+0.12,w:nodes[i+1][0]-nodes[i][0],h:nodes[i+1][1]-nodes[i][1],line:{color:TEAL,width:1.5,transparency:35}});
nodes.forEach((n,i)=>s.addShape(p.shapes.OVAL,{x:n[0],y:n[1],w:0.24,h:0.24,fill:{color:i%2?RED:TEAL}}));
s.addText("Seminário de Algoritmos Bioinspirados  -  2026",{x:0.7,y:1.05,w:8,h:0.4,fontFace:FB,fontSize:14,color:"9FB6BC",charSpacing:1});
s.addText("Alocação de Máquinas Virtuais na Nuvem",{x:0.7,y:1.55,w:8.6,h:1.0,fontFace:FH,fontSize:38,bold:true,color:WHITE,margin:0});
s.addText("Otimização bioobjetivo com Colônia de Formigas (VMPACS)",{x:0.7,y:2.7,w:8.2,h:0.6,fontFace:FB,fontSize:19,italic:true,color:"CADCDF",margin:0});
s.addShape(p.shapes.LINE,{x:0.72,y:3.55,w:3.2,h:0,line:{color:TEAL,width:2}});
s.addText([{text:"Energia",options:{color:TEAL,bold:true}},{text:"  x  ",options:{color:"9FB6BC"}},{text:"Desperdício de recursos",options:{color:RED,bold:true}}],{x:0.7,y:3.7,w:8,h:0.4,fontFace:FB,fontSize:16,margin:0});
s.addText("Lucas Rivetti   e   Ian Nunes",{x:0.7,y:4.7,w:8.6,h:0.4,fontFace:FB,fontSize:14,color:"9FB6BC"});
s.addNotes("Apresentar o tema: alocação de VMs em data centers, otimizando energia e desperdício ao mesmo tempo, com colônia de formigas (VMPACS), baseado em Gao et al. (2013).");
rodape(s,1,true);

// 2 PROBLEMA
s=p.addSlide(); s.background={color:WHITE};
header(s,"1","O problema: alocação de VMs");
card(s,0.5,1.2,4.6,3.9,LIGHT);
s.addText("O que é?",{x:0.8,y:1.4,w:4,h:0.4,fontFace:FH,fontSize:17,bold:true,color:TEAL,margin:0});
bullets(s,["Decidir em qual servidor físico cada máquina virtual (VM) será executada.","Consolidar VMs em poucos servidores e desligar os ociosos economiza energia.","Mas servidores mal balanceados (CPU cheia, memória vazia) desperdiçam recursos.","É uma variante do empacotamento vetorial: NP-difícil (m^n alocações possíveis)."],0.8,1.85,4.05,3.1,13.5);
card(s,5.4,1.2,4.1,3.9,WHITE);
s.addText("Consolidação",{x:5.6,y:1.35,w:3.6,h:0.35,fontFace:FH,fontSize:16,bold:true,color:DARK,margin:0});
s.addText("Antes: 7 servidores subutilizados",{x:5.6,y:1.75,w:3.7,h:0.3,fontFace:FB,fontSize:11,color:MUTED,margin:0});
for(let i=0;i<7;i++){ s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:5.62+i*0.52,y:2.1,w:0.42,h:0.42,rectRadius:0.05,fill:{color:"D6E2E4"},line:{color:SLATE,width:0.75}}); s.addShape(p.shapes.OVAL,{x:5.74+i*0.52,y:2.27,w:0.18,h:0.18,fill:{color:SLATE}});}
s.addShape(p.shapes.LINE,{x:7.45,y:2.75,w:0,h:0.5,line:{color:TEAL,width:2.5,endArrowType:"triangle"}});
s.addText("Depois: 3 servidores bem ocupados",{x:5.6,y:3.35,w:3.7,h:0.3,fontFace:FB,fontSize:11,color:MUTED,margin:0});
for(let i=0;i<3;i++){ s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:5.8+i*1.15,y:3.7,w:0.95,h:0.95,rectRadius:0.06,fill:{color:"D2ECE9"},line:{color:TEAL,width:1}}); for(let k=0;k<4;k++) s.addShape(p.shapes.OVAL,{x:5.93+i*1.15+(k%2)*0.38,y:3.83+Math.floor(k/2)*0.38,w:0.26,h:0.26,fill:{color:TEAL}});}
s.addNotes("Consolidação: agrupar VMs para ligar menos máquinas, sem desbalancear CPU e memória.");
rodape(s,2,false);

// 3 MULTIOBJETIVO
s=p.addSlide(); s.background={color:WHITE};
header(s,"2","Dois objetivos em conflito");
card(s,0.5,1.3,4.45,2.7,WHITE);
s.addShape(p.shapes.OVAL,{x:0.8,y:1.55,w:0.6,h:0.6,fill:{color:TEAL}});
s.addText("E",{x:0.8,y:1.55,w:0.6,h:0.6,align:"center",valign:"middle",fontFace:FH,bold:true,fontSize:22,color:WHITE,margin:0});
s.addText("Consumo de energia",{x:1.55,y:1.6,w:3.2,h:0.5,fontFace:FH,fontSize:18,bold:true,color:DARK,margin:0,valign:"middle"});
bullets(s,["Potência cresce linear com o uso de CPU.","Servidores ociosos são desligados.","Minimizar energia ~ usar menos servidores."],0.85,2.35,3.9,1.5,13.5);
card(s,5.05,1.3,4.45,2.7,WHITE);
s.addShape(p.shapes.OVAL,{x:5.35,y:1.55,w:0.6,h:0.6,fill:{color:RED}});
s.addText("W",{x:5.35,y:1.55,w:0.6,h:0.6,align:"center",valign:"middle",fontFace:FH,bold:true,fontSize:22,color:WHITE,margin:0});
s.addText("Desperdício de recursos",{x:6.1,y:1.6,w:3.2,h:0.5,fontFace:FH,fontSize:18,bold:true,color:DARK,margin:0,valign:"middle"});
bullets(s,["Penaliza desbalanceamento entre CPU e memória.","Servidores muito cheios ou vazios desperdiçam.","Minimizar = empacotar de forma equilibrada."],5.4,2.35,3.9,1.5,13.5);
card(s,0.5,4.2,9.0,0.95,DARK);
s.addText([{text:"Conflito:  ",options:{bold:true,color:WHITE}},{text:"reduzir servidores pode desbalancear -> buscamos o conjunto de melhores compromissos (a ",options:{color:"CADCDF"}},{text:"fronteira de Pareto",options:{bold:true,color:TEAL}},{text:").",options:{color:"CADCDF"}}],{x:0.85,y:4.2,w:8.3,h:0.95,fontFace:FB,fontSize:15,valign:"middle",margin:0});
s.addNotes("Os dois objetivos competem: a resposta é um conjunto de soluções não-dominadas (fronteira de Pareto).");
rodape(s,3,false);

// 4 FORMULACAO
s=p.addSlide(); s.background={color:WHITE};
header(s,"3","Formulação matemática");
card(s,0.5,1.25,9.0,2.7,LIGHT);
s.addImage({path:"/tmp/proj/img_formulacao.png",x:0.9,y:1.45,w:8.2,h:2.3,sizing:{type:"contain",w:8.2,h:2.3}});
s.addText([{text:"Variáveis binárias:  ",options:{bold:true,color:DARK}},{text:"x",options:{italic:true,color:INK}},{text:"ij",options:{italic:true,color:INK,subscript:true}},{text:" = VM i no servidor j;   ",options:{color:INK}},{text:"y",options:{italic:true,color:INK}},{text:"j",options:{italic:true,color:INK,subscript:true}},{text:" = servidor j em uso.   Limites T",options:{color:INK}},{text:" = 90%   |   P_idle=162W, P_busy=215W.",options:{color:INK}}],{x:0.6,y:4.2,w:8.8,h:0.7,fontFace:FB,fontSize:14,align:"center",valign:"middle",margin:0});
s.addNotes("f1 = energia (nº de servidores ligados). f2 = desperdício (desbalanceamento CPU/memória). Restrições: cada VM em 1 servidor e limites de capacidade.");
rodape(s,4,false);

// 5 VMPACS IDEIA
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.OVAL,{x:0.5,y:0.4,w:0.55,h:0.55,fill:{color:TEAL}});
s.addText("4",{x:0.5,y:0.4,w:0.55,h:0.55,align:"center",valign:"middle",fontFace:FH,fontSize:20,bold:true,color:WHITE,margin:0});
s.addText("VMPACS: a metáfora das formigas",{x:1.2,y:0.38,w:8.4,h:0.6,fontFace:FH,fontSize:26,bold:true,color:WHITE,margin:0,valign:"middle"});
s.addText("Formigas depositam feromônio nos bons caminhos; caminhos bons atraem mais formigas. Aqui, cada formiga constrói uma alocação e reforça os bons movimentos (VM -> servidor).",{x:0.6,y:1.15,w:8.9,h:0.7,fontFace:FB,fontSize:15,italic:true,color:"CADCDF",margin:0});
const items5=[["Feromônio (tau)","Memória do que funcionou: movimentos usados por boas soluções ganham mais feromônio.",TEAL],["Heurística (eta)","Conhecimento do problema: prioriza movimentos que poupam energia e equilibram recursos.",RED],["Arquivo de Pareto","Guarda as soluções não-dominadas; só elas reforçam o feromônio (atualização global).","6AA9AE"]];
const glyph5=["τ","η","P"];
items5.forEach((it,i)=>{ const x=0.5+i*3.07;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y:2.05,w:2.9,h:2.9,rectRadius:0.08,fill:{color:"1C3F49"}});
  s.addShape(p.shapes.OVAL,{x:x+0.25,y:2.3,w:0.62,h:0.62,fill:{color:it[2]}});
  s.addText(glyph5[i],{x:x+0.25,y:2.3,w:0.62,h:0.62,align:"center",valign:"middle",fontFace:FH,fontSize:20,bold:true,color:WHITE,margin:0});
  s.addText(it[0],{x:x+0.22,y:3.0,w:2.5,h:0.6,fontFace:FH,fontSize:16,bold:true,color:WHITE,margin:0});
  s.addText(it[1],{x:x+0.22,y:3.55,w:2.5,h:1.3,fontFace:FB,fontSize:12.5,color:"CADCDF",margin:0,valign:"top"});});
s.addNotes("Três ingredientes: feromônio (aprendizado), heurística (guia do problema) e o arquivo de Pareto com as melhores soluções.");
rodape(s,5,true);

// 6 VMPACS FUNCIONAMENTO
s=p.addSlide(); s.background={color:WHITE};
header(s,"5","VMPACS: como uma formiga constrói");
const steps=[["1","Abre um servidor","Começa um novo servidor (host) para receber VMs."],["2","Escolhe a próxima VM","Regra pseudoaleatória: combina feromônio + heurística (q0=0.8 intensifica, senão explora)."],["3","Atualização local","Após cada movimento, evapora um pouco do feromônio para diversificar."],["4","Atualização global","No fim da iteração, as soluções de Pareto reforçam seus movimentos."]];
steps.forEach((st,i)=>{ const y=1.25+i*0.97;
  s.addShape(p.shapes.OVAL,{x:0.6,y:y,w:0.62,h:0.62,fill:{color:i<3?TEAL:RED}});
  s.addText(st[0],{x:0.6,y:y,w:0.62,h:0.62,align:"center",valign:"middle",fontFace:FH,fontSize:20,bold:true,color:WHITE,margin:0});
  s.addText(st[1],{x:1.4,y:y-0.02,w:3.6,h:0.45,fontFace:FH,fontSize:16,bold:true,color:DARK,margin:0,valign:"middle"});
  s.addText(st[2],{x:1.4,y:y+0.35,w:3.55,h:0.55,fontFace:FB,fontSize:12.5,color:MUTED,margin:0,valign:"top"});});
card(s,5.25,1.25,4.25,3.6,LIGHT);
s.addText("Regra de escolha do movimento",{x:5.5,y:1.45,w:3.8,h:0.4,fontFace:FH,fontSize:15,bold:true,color:DARK,margin:0});
s.addText([{text:"intensificar (q <= q0):",options:{bold:true,color:TEAL,breakLine:true}},{text:"escolhe o movimento com maior",options:{color:INK,breakLine:true}},{text:"   alpha*tau + (1-alpha)*eta",options:{italic:true,color:INK,breakLine:true}},{text:" ",options:{breakLine:true,fontSize:6}},{text:"explorar (q > q0):",options:{bold:true,color:RED,breakLine:true}},{text:"sorteia proporcional a esse valor.",options:{color:INK,breakLine:true}},{text:" ",options:{breakLine:true,fontSize:6}},{text:"Repete até alocar todas as VMs; cada formiga gera uma solução completa.",options:{color:MUTED,italic:true}}],{x:5.5,y:1.9,w:3.75,h:2.8,fontFace:FB,fontSize:13.5,valign:"top",margin:0,paraSpaceAfter:3});
s.addNotes("Construção gulosa-probabilística: enche um servidor de cada vez, escolhendo VMs por feromônio+heurística, até alocar todas.");
rodape(s,6,false);

// 7 NSGA-II
s=p.addSlide(); s.background={color:WHITE};
header(s,"6","Comparação: NSGA-II");
s.addText("Algoritmo genético multiobjetivo mais usado (Deb et al., 2002) - assim como o artigo compara o VMPACS com um algoritmo genético.",{x:0.6,y:1.15,w:8.9,h:0.55,fontFace:FB,fontSize:14,italic:true,color:MUTED,margin:0});
const mech=[["Ordenação não-dominada","Classifica a população em frentes de Pareto sucessivas (frente 0 = melhores).",TEAL],["Distância de multidão","Mede o isolamento de cada solução para manter a fronteira bem espalhada (diversidade).",RED]];
mech.forEach((m,i)=>{ const x=0.5+i*4.6;
  card(s,x,1.85,4.3,1.7,LIGHT);
  s.addShape(p.shapes.OVAL,{x:x+0.25,y:2.05,w:0.5,h:0.5,fill:{color:m[2]}});
  s.addText(String(i+1),{x:x+0.25,y:2.05,w:0.5,h:0.5,align:"center",valign:"middle",fontFace:FH,bold:true,fontSize:17,color:WHITE,margin:0});
  s.addText(m[0],{x:x+0.9,y:2.05,w:3.2,h:0.5,fontFace:FH,fontSize:15,bold:true,color:DARK,margin:0,valign:"middle"});
  s.addText(m[1],{x:x+0.28,y:2.65,w:3.85,h:0.8,fontFace:FB,fontSize:13,color:INK,margin:0,valign:"top"});});
card(s,0.5,3.75,9.0,1.25,WHITE);
s.addText([{text:"Codificação:  ",options:{bold:true,color:DARK}},{text:"cada indivíduo é uma permutação das VMs, decodificada por first-fit (sempre válida). ",options:{color:INK}},{text:"Operadores:  ",options:{bold:true,color:DARK}},{text:"Order Crossover (OX) + mutação por troca; seleção por torneio e elitismo.",options:{color:INK}}],{x:0.8,y:3.75,w:8.4,h:1.25,fontFace:FB,fontSize:14,valign:"middle",margin:0});
s.addNotes("NSGA-II: ordenação por não-dominância + crowding. Codificação por permutação com decodificador first-fit.");
rodape(s,7,false);

// 8 METODOLOGIA
s=p.addSlide(); s.background={color:WHITE};
header(s,"7","Metodologia experimental");
const meto=[["Instâncias","n = 100 VMs e 100 servidores; 5 níveis de correlação CPU/memória (P de 0 a 1); limites de 90%."],["Parâmetros","VMPACS: 10 formigas x 100 iterações. NSGA-II: pop. 50 x 20 gerações. ~1000 avaliações cada (justo)."],["Métricas (4)","Hipervolume e IGD (convergência), ONVG (cardinalidade), Spacing (uniformidade)."],["Execuções","10 repetições independentes por configuração; média +/- desvio-padrão."]];
meto.forEach((m,i)=>{ const x=0.5+(i%2)*4.65, y=1.3+Math.floor(i/2)*1.85;
  card(s,x,y,4.35,1.65,LIGHT);
  s.addShape(p.shapes.OVAL,{x:x+0.25,y:y+0.22,w:0.5,h:0.5,fill:{color:[TEAL,RED,SLATE,"6AA9AE"][i]}});
  s.addText(["I","P","M","R"][i],{x:x+0.25,y:y+0.22,w:0.5,h:0.5,align:"center",valign:"middle",fontFace:FH,bold:true,fontSize:18,color:WHITE,margin:0});
  s.addText(m[0],{x:x+0.9,y:y+0.2,w:3.2,h:0.5,fontFace:FH,fontSize:15,bold:true,color:DARK,margin:0,valign:"middle"});
  s.addText(m[1],{x:x+0.3,y:y+0.75,w:3.85,h:0.8,fontFace:FB,fontSize:12.5,color:INK,margin:0,valign:"top"});});
s.addNotes("100 VMs, 5 correlações, orçamentos equiparados em ~1000 avaliações, 4 métricas, 10 execuções.");
rodape(s,8,false);

// 9 RESULTADOS 1
s=p.addSlide(); s.background={color:WHITE};
header(s,"8","Resultados: energia e desperdício");
s.addImage({path:FIG+"energia_barras.png",x:0.4,y:1.25,w:4.6,h:2.95,sizing:{type:"contain",w:4.6,h:2.95}});
s.addImage({path:FIG+"desperdicio_barras.png",x:5.0,y:1.25,w:4.6,h:2.95,sizing:{type:"contain",w:4.6,h:2.95}});
card(s,0.5,4.35,9.0,0.85,DARK);
s.addText([{text:"Leitura:  ",options:{bold:true,color:TEAL}},{text:"o NSGA-II atinge menor energia em 4 de 5 cenários e menor desperdício em 4 de 5 (exceção em P=0.5).",options:{color:"E8EFF0"}}],{x:0.85,y:4.35,w:8.3,h:0.85,fontFace:FB,fontSize:14,valign:"middle",margin:0});
s.addNotes("Barras de energia e desperdício por correlação. NSGA-II em geral leva vantagem; em P=0.5 o VMPACS empata/ganha no desperdício.");
rodape(s,9,false);

// 10 RESULTADOS 2
s=p.addSlide(); s.background={color:WHITE};
header(s,"9","Resultados: métricas multiobjetivo");
s.addImage({path:FIG+"hipervolume_barras.png",x:0.35,y:1.2,w:3.25,h:2.1,sizing:{type:"contain",w:3.25,h:2.1}});
s.addImage({path:FIG+"igd_barras.png",x:3.7,y:1.2,w:3.25,h:2.1,sizing:{type:"contain",w:3.25,h:2.1}});
card(s,7.1,1.2,2.5,2.1,LIGHT);
s.addText("Convergência",{x:7.25,y:1.35,w:2.2,h:0.4,fontFace:FH,fontSize:14,bold:true,color:DARK,margin:0});
bullets(s,["HV maior = melhor","IGD menor = melhor","trade-off real e raso"],7.25,1.75,2.25,1.4,12);
s.addImage({path:"/tmp/proj/fronteiras_slide.png",x:0.35,y:3.3,w:9.3,h:1.95,sizing:{type:"contain",w:9.3,h:1.95}});
s.addNotes("A curva cinza e a fronteira REAL (melhor conhecida): trade-off existe, porem raso. Os algoritmos convergem para o joelho de menor energia; o NSGA-II encosta na fronteira e o VMPACS fica um pouco acima.");
rodape(s,10,false);

// 11 DISCUSSAO
s=p.addSlide(); s.background={color:WHITE};
header(s,"10","Discussão");
const disc=[["Convergência","NSGA-II converge para menor energia e desperdício (maior HV, menor IGD) na maioria dos casos.",TEAL],["Diversidade","VMPACS encontra mais soluções não-dominadas (ONVG) em correlações negativas.",RED],["Fronteira compacta","Empacotar bem reduz energia E desperdício juntos: objetivos quase alinhados.",SLATE],["Correlação importa","P=0.75 (CPU e mem. altas juntas) gera o maior desperdício; balancear fica difícil.","6AA9AE"]];
disc.forEach((d,i)=>{ const y=1.3+i*0.92;
  s.addShape(p.shapes.OVAL,{x:0.6,y:y+0.05,w:0.4,h:0.4,fill:{color:d[2]}});
  s.addText(d[0],{x:1.2,y:y,w:2.7,h:0.5,fontFace:FH,fontSize:15.5,bold:true,color:DARK,margin:0,valign:"middle"});
  s.addText(d[1],{x:3.95,y:y,w:5.55,h:0.55,fontFace:FB,fontSize:13.5,color:INK,margin:0,valign:"middle"});});
s.addNotes("Pontos principais: NSGA-II converge melhor; VMPACS mais diverso em correlação negativa; objetivos quase alinhados; efeito da correlação.");
rodape(s,11,false);

// 12 CONCLUSOES
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.OVAL,{x:0.5,y:0.4,w:0.55,h:0.55,fill:{color:TEAL}});
s.addText("11",{x:0.5,y:0.4,w:0.55,h:0.55,align:"center",valign:"middle",fontFace:FH,fontSize:18,bold:true,color:WHITE,margin:0});
s.addText("Conclusões",{x:1.2,y:0.38,w:8,h:0.6,fontFace:FH,fontSize:26,bold:true,color:WHITE,margin:0,valign:"middle"});
const conc=["Implementamos o VMPACS (colônia de formigas) e o NSGA-II no problema bioobjetivo de alocação de VMs.","Com orçamentos iguais, o NSGA-II convergiu melhor; o VMPACS ofereceu fronteiras um pouco mais diversas.","Para estas instâncias os objetivos são quase alinhados, gerando fronteiras de Pareto compactas - um resultado instrutivo."];
conc.forEach((c,i)=>{ const y=1.45+i*0.92;
  s.addShape(p.shapes.OVAL,{x:0.7,y:y,w:0.45,h:0.45,fill:{color:TEAL}});
  s.addText(String(i+1),{x:0.7,y:y,w:0.45,h:0.45,align:"center",valign:"middle",fontFace:FH,bold:true,fontSize:16,color:WHITE,margin:0});
  s.addText(c,{x:1.35,y:y-0.1,w:8.1,h:0.7,fontFace:FB,fontSize:15,color:"E8EFF0",margin:0,valign:"middle"});});
card(s,0.7,4.35,8.75,0.78,"1C3F49");
s.addText([{text:"Trabalhos futuros:  ",options:{bold:true,color:TEAL}},{text:"instâncias maiores (n=2000), servidores heterogêneos e versão memética do VMPACS (com busca local).",options:{color:"CADCDF"}}],{x:1.0,y:4.35,w:8.2,h:0.78,fontFace:FB,fontSize:13.5,valign:"middle",margin:0});
s.addNotes("Fechar com os três aprendizados e os trabalhos futuros.");
rodape(s,12,true);

// 13 REFERENCIAS
s=p.addSlide(); s.background={color:DARK};
s.addShape(p.shapes.OVAL,{x:0.5,y:0.4,w:0.55,h:0.55,fill:{color:TEAL}});
s.addText("12",{x:0.5,y:0.4,w:0.55,h:0.55,align:"center",valign:"middle",fontFace:FH,fontSize:18,bold:true,color:WHITE,margin:0});
s.addText("Referências",{x:1.2,y:0.38,w:8,h:0.6,fontFace:FH,fontSize:26,bold:true,color:WHITE,margin:0,valign:"middle"});
const refs=[
 "[1] Gao, Guan, Qi, Hou, Liu (2013). A multi-objective ant colony system algorithm for virtual machine placement in cloud computing. J. of Computer and System Sciences, 79(8), 1230-1242.",
 "[2] Deb, Pratap, Agarwal, Meyarivan (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE Trans. on Evolutionary Computation, 6(2), 182-197.",
 "[3] Dorigo, Gambardella (1997). Ant colony system: a cooperative learning approach to the TSP. IEEE Trans. on Evolutionary Computation, 1(1), 53-66.",
 "[4] Zitzler, Thiele (1999). Multiobjective evolutionary algorithms: a comparative case study and the strength Pareto approach. IEEE Trans. on Evol. Computation, 3(4), 257-271.",
 "[5] Van Veldhuizen (1999). Multiobjective Evolutionary Algorithms: Classifications, Analyses, and New Innovations. PhD thesis, Air Force Institute of Technology."];
s.addText(refs.map((t)=>({text:t,options:{breakLine:true,paraSpaceAfter:11,color:"E8EFF0",fontSize:14}})),{x:0.7,y:1.4,w:8.8,h:3.7,fontFace:FB,valign:"top",margin:0});
s.addText("Obrigado!  Perguntas?",{x:0.7,y:5.0,w:8.6,h:0.4,fontFace:FH,fontSize:15,bold:true,italic:true,color:TEAL,margin:0});
s.addNotes("Slide de fechamento: agradecer e abrir para perguntas.");
rodape(s,13,true);

p.writeFile({fileName:"/tmp/proj/slides.pptx"}).then(()=>console.log("PPTX gerado: 13 slides"));
