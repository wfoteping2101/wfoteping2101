"""La Richesse Silencieuse: the section shown on the book's main page, between the opening and the chapters.
It explains the book, why investing matters (with the book's own figures), and carries a small sample of the
investment simulator at /demo/simulateur-placements."""

SIM = "/demo/simulateur-placements"

STYLE = """<style>
.rs-intro{padding-block:clamp(26px,5vw,60px) clamp(10px,2vw,24px)}
.rs-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:clamp(20px,4vw,48px);align-items:start}
@media (max-width:900px){.rs-grid{grid-template-columns:minmax(0,1fr)}}
.rs-intro h2{font-size:clamp(28px,3.6vw,44px);margin:14px 0 14px}
.rs-intro .lede{margin-bottom:14px}
.rs-parts{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:8px;counter-reset:p}
.rs-parts li{display:grid;grid-template-columns:34px minmax(0,1fr);gap:8px;font-size:15px;color:var(--encre);counter-increment:p}
.rs-parts li::before{content:counter(p,upper-roman);font:italic 400 18px/1.35 var(--serif);color:var(--or)}
.rs-why{margin-top:clamp(26px,4vw,40px)}
.rs-why h3{font-size:clamp(22px,2.6vw,30px);margin:12px 0 12px}
.rs-facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media (max-width:640px){.rs-facts{grid-template-columns:minmax(0,1fr)}}
.rs-fact{border:1px solid var(--ligne);border-radius:var(--r);padding:14px 16px;background:var(--blanc)}
.rs-fact b{display:block;font:400 26px/1.1 var(--serif);color:var(--fusain);margin:4px 0 6px;font-variant-numeric:tabular-nums}
.rs-fact span.k{font:600 11px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--or)}
.rs-fact p{margin:0;font-size:14.5px;color:var(--encre)}
.rs-note{font-size:13.5px;color:var(--gris);margin:12px 0 0;max-width:70ch}
.rs-sample{border:1px solid var(--ligne);border-radius:18px;background:var(--blanc);padding:clamp(16px,2.4vw,24px);position:sticky;top:84px}
@media (max-width:900px){.rs-sample{position:static}}
.rs-sample h3{font-size:24px;margin:10px 0 6px}
.rs-sample .sub{font-size:14px;color:var(--gris);margin:0 0 14px}
.rs-in{display:grid;gap:12px;margin-bottom:14px}
.rs-in label{display:grid;gap:4px;font-size:14px;color:var(--encre)}
.rs-in .rs-top{display:flex;justify-content:space-between;gap:10px;align-items:baseline}
.rs-in output{font:600 14px var(--mono);color:var(--fusain);font-variant-numeric:tabular-nums}
.rs-in input[type=range]{width:100%;accent-color:#0F6B4E}
.rs-bars{display:grid;gap:9px;margin:6px 0 12px}
.rs-bar{display:grid;grid-template-columns:minmax(0,8.5em) minmax(0,1fr) minmax(0,6.2em);gap:10px;align-items:center;font-size:13.5px}
.rs-bar .t{color:var(--encre)}
.rs-bar .w{position:relative;height:14px;border-radius:7px;background:var(--craie-2);overflow:hidden}
.rs-bar .w i{position:absolute;inset:0 auto 0 0;border-radius:7px;background:var(--pierre);transition:width .35s var(--ease)}
.rs-bar em{font:600 12.5px var(--mono);font-style:normal;color:var(--fusain);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.rs-bar.c5 .w i{background:#8FA197}.rs-bar.c7 .w i{background:#0F6B4E}.rs-bar.c9 .w i{background:#C89B3C}.rs-bar.sv .w i{background:var(--ligne)}
.rs-bar.c7 em{color:#0F6B4E}
:root[data-theme="dark"] .rs-bar.c7 em{color:#6FD0AA}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .rs-bar.c7 em{color:#6FD0AA}}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .rs-bar.c7 .w i{background:#3E9E7C}}
:root[data-theme="dark"] .rs-bar.c7 .w i{background:#3E9E7C}
.rs-line{font-size:14.5px;color:var(--encre);margin:0 0 12px}
.rs-line b{font-variant-numeric:tabular-nums}
.rs-sample .btn{width:100%;justify-content:center}
@media (prefers-reduced-motion:reduce){.rs-bar .w i{transition:none}}
</style>"""

SCRIPT = """<script>
(function(){
  var root=document.querySelector('.rs-sample'); if(!root) return;
  var m=root.querySelector('#rs-m'), a=root.querySelector('#rs-a'), r=root.querySelector('#rs-r');
  function fr(){ return document.documentElement.lang==='fr'; }
  function money(v){ var s=Math.abs(v)>=1e4?100:10; v=Math.round(v/s)*s; return fr()?new Intl.NumberFormat('fr-FR').format(v)+' $':'$'+new Intl.NumberFormat('en-US').format(v); }
  function fv(pmt,rate,n){ var g=rate/100, v=0; for(var i=0;i<n;i++) v=v*(1+g)+pmt; return v; }
  function draw(){
    var mo=+m.value, start=+a.value, ret=+r.value; if(ret<=start){ ret=start+1; r.value=ret; }
    var n=ret-start, pmt=mo*12;
    root.querySelector('#rs-mo').textContent=money(mo)+(fr()?' par mois':' a month');
    root.querySelector('#rs-ao').textContent=start+(fr()?' ans':'');
    root.querySelector('#rs-ro').textContent=ret+(fr()?' ans':'');
    var vals={paid:pmt*n, sv:fv(pmt,1,n), c5:fv(pmt,5,n), c7:fv(pmt,7,n), c9:fv(pmt,9,n)}, max=vals.c9;
    Object.keys(vals).forEach(function(k){ var b=root.querySelector('[data-k="'+k+'"]'); b.querySelector('i').style.width=Math.max(2,100*vals[k]/max)+'%'; b.querySelector('em').textContent=money(vals[k]); });
    var x=Math.pow(1.07,n), xs=new Intl.NumberFormat(fr()?'fr-FR':'en-US',{maximumFractionDigits:1}).format(x);
    root.querySelector('#rs-line').innerHTML=fr()
      ? 'À 7 % par an, chaque dollar versé à '+start+' ans devient environ <b>'+xs+'</b> dollars à '+ret+' ans. Sur un compte à 1 %, les mêmes versements donnent <b>'+money(vals.sv)+'</b>.'
      : 'At 7% a year, each dollar contributed at '+start+' becomes about <b>'+xs+'</b> dollars at '+ret+'. In an account paying 1%, the same contributions give <b>'+money(vals.sv)+'</b>.';
    var link=root.querySelector('#rs-open'); link.href='""" + SIM + """#acc=index&cur=USD&age='+start+'&ret='+ret+'&stop='+ret+'&monthly='+mo+'&fee=0.05';
  }
  [m,a,r].forEach(function(el){ el.addEventListener('input',draw); });
  addEventListener('wf-lang',draw);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',draw); else draw();
})();
</script>"""


def section(t):
    parts = [
        ("Live below your means, even with an extended family: a fixed share of income goes to the future, another to the family, before anything else.",
         "Choisir un mode de vie financier sain : une part fixe du revenu pour l'avenir, une autre pour la famille, avant tout le reste."),
        ("Understand what you buy: shares, bonds, funds, and why indexing wins.",
         "Comprendre ce que l'on achète : actions, obligations, fonds, et pourquoi l'indexation gagne."),
        ("Build a simple portfolio: asset allocation, global diversification, low fees, taxes, automatic rebalancing.",
         "Construire un portefeuille simple : allocation d'actifs, diversification mondiale, frais bas, impôts, rééquilibrage automatique."),
        ("The investor and their behaviour: fear, noise, visible wealth, helping relatives without ruining yourself, and a grid to judge an investment back home.",
         "L'investisseur et son comportement : la peur, le bruit, la richesse visible, aider les siens sans se ruiner, et une grille pour juger un investissement au pays."),
        ("Property, here and there: the home, rentals, and a full checklist for a project in Africa.",
         "L'immobilier, ici et là-bas : la résidence principale, le locatif, et une checklist complète pour un projet en Afrique."),
        ("Protect, prepare, pass on: insurance, children's education, retirement, withdrawals, wills and beneficiaries.",
         "Protéger, préparer, transmettre : assurances, études des enfants, retraite, retraits, testament et bénéficiaires."),
    ]
    facts = [
        ("Time", "Le temps", "15×", "× 15",
         "At 7% a year, money doubles about every ten years. A dollar invested at 25 becomes about 15 dollars at 65; invested at 45, about 4.",
         "À 7 % par an, un capital double environ tous les dix ans. Un dollar placé à 25 ans devient environ 15 dollars à 65 ans ; placé à 45 ans, environ 4."),
        ("Inflation", "L'inflation", "$4,100", "4 100 $",
         "At 3% inflation, $10,000 left without a return for thirty years buys only what $4,100 buys today.",
         "À 3 % d'inflation, 10 000 dollars laissés sans rendement pendant trente ans n'achètent plus que l'équivalent de 4 100 dollars d'aujourd'hui."),
        ("Fees", "Les frais", "$175,000", "175 000 $",
         "On $12,000 a year for thirty years, a fund charging 1% instead of an index fund at 0.05% costs about $175,000.",
         "Sur 12 000 dollars par an pendant trente ans, un fonds à 1 % de frais au lieu d'un fonds indiciel à 0,05 % coûte environ 175 000 dollars."),
        ("The employer", "L'employeur", "$170,000", "170 000 $",
         "Salary $60,000, a 6% contribution and 3% from the employer: after thirty years at 7%, the employer's part alone is worth about $170,000.",
         "Salaire de 60 000 dollars, 6 % de cotisation et 3 % de l'employeur : après trente ans à 7 %, la part de l'employeur seule vaut environ 170 000 dollars."),
    ]
    parts_html = "".join(f"<li><span>{t(en, fr)}</span></li>" for en, fr in parts)
    facts_html = "".join(
        f'<div class="rs-fact rv"><span class="k">{t(ken, kfr)}</span><b>{t(ven, vfr)}</b><p>{t(en, fr)}</p></div>'
        for ken, kfr, ven, vfr, en, fr in facts)
    bars = "".join(
        f'<div class="rs-bar {k}" data-k="{k}"><span class="t">{t(en, fr)}</span><span class="w"><i style="width:0"></i></span><em></em></div>'
        for k, en, fr in [("paid", "Contributed", "Total versé"), ("sv", "Savings at 1%", "Épargne à 1\u00a0%"),
                          ("c5", "Index fund 5%", "Indiciel 5\u00a0%"), ("c7", "Index fund 7%", "Indiciel 7\u00a0%"),
                          ("c9", "Index fund 9%", "Indiciel 9\u00a0%")])
    return STYLE + f"""<section class="rs-intro wrap" id="pourquoi-investir"><div class="rs-grid">
<div>
<span class="label rv"><b>{t('About the book', 'Le livre')}</b><span>{t('Investing guide', "Guide d'investissement")}</span></span>
<h2 class="rv">{t('Invest for later without abandoning the family.', 'Investir pour demain sans abandonner les siens.')}</h2>
<p class="lede rv">{t("La Richesse Silencieuse is written for salaried members of the African diaspora in North America and Europe: people who earn a good living, send money home every month, and keep hearing that they must build back there first. The book does not ask them to give less. It asks them to give within a set limit, and to put a fixed share of every pay cheque to work in low-cost index funds, through the accounts their country offers: 401(k), 403(b), IRA, PER, PEA, RRSP, TFSA.", "La Richesse Silencieuse s'adresse aux salariés de la diaspora africaine en Amérique du Nord et en Europe : ceux qui gagnent bien leur vie, envoient de l'argent au pays chaque mois, et entendent sans cesse qu'il faut d'abord construire là-bas. Le livre ne leur demande pas de donner moins. Il leur demande de donner dans une limite fixée, et de faire travailler une part fixe de chaque salaire dans des fonds indiciels à bas coût, par les comptes que leur pays propose : 401(k), 403(b), IRA, PER, PEA, REER, CELI.")}</p>
<p class="rv" style="color:var(--encre)">{t('Six parts, 28 chapters, each ending with questions for discussion:', 'Six parties, 28 chapitres, chacun terminé par des questions de discussion :')}</p>
<ol class="rs-parts rv">{parts_html}</ol>
<div class="rs-why">
<span class="label rv"><b>{t('Why invest', 'Pourquoi investir')}</b><span>{t("The book's figures", 'Les chiffres du livre')}</span></span>
<h3 class="rv">{t('A salary stops one day. Capital keeps working.', 'Un salaire s’arrête un jour. Un capital continue de travailler.')}</h3>
<p class="rv" style="color:var(--encre);max-width:62ch">{t('Saving is not enough: money that sleeps loses value to inflation, and every year of waiting removes years of growth. Four numbers from the book show what is at stake.', "Épargner ne suffit pas : l'argent qui dort perd de sa valeur à cause de l'inflation, et chaque année d'attente retire des années de croissance. Quatre chiffres du livre montrent l'enjeu.")}</p>
<div class="rs-facts">{facts_html}</div>
<p class="rs-note rv">{t('The 5, 7 and 9% returns used in the book and below are teaching assumptions, before inflation, never guarantees.', 'Les rendements de 5, 7 et 9 % utilisés dans le livre et ci-contre sont des hypothèses pédagogiques, avant inflation, jamais des garanties.')}</p>
</div>
</div>
<aside class="rs-sample rv" aria-labelledby="rs-h">
<span class="label"><b>{t('Sample', 'Exemple')}</b><span>{t('Investment simulator', 'Simulateur de placements')}</span></span>
<h3 id="rs-h">{t('What do your contributions become?', 'Que deviennent vos versements ?')}</h3>
<p class="sub">{t('Move the sliders. One contribution a year, as in the book, no fees. 7% is the central scenario.', 'Déplacez les curseurs. Un versement par an, comme dans le livre, sans frais. 7 % est le scénario central.')}</p>
<div class="rs-in">
<label><span class="rs-top"><span>{t('Monthly contribution', 'Versement mensuel')}</span><output id="rs-mo"></output></span><input id="rs-m" type="range" min="50" max="2000" step="50" value="300"></label>
<label><span class="rs-top"><span>{t('Start age', 'Âge de départ')}</span><output id="rs-ao"></output></span><input id="rs-a" type="range" min="18" max="60" step="1" value="25"></label>
<label><span class="rs-top"><span>{t('Withdrawal age', 'Âge de retrait')}</span><output id="rs-ro"></output></span><input id="rs-r" type="range" min="40" max="75" step="1" value="65"></label>
</div>
<div class="rs-bars">{bars}</div>
<p class="rs-line" id="rs-line"></p>
<p class="muted" style="font-size:13px;margin:0 0 14px">{t("Book, chapter 3: $300 a month from 25 to 65 gives about $719,000 in the central scenario.", 'Livre, chapitre 3 : 300 $ par mois de 25 à 65 ans donnent environ 719 000 $ dans le scénario central.')}</p>
<a class="btn" id="rs-open" href="{SIM}">{t('Open the full simulator', 'Ouvrir le simulateur complet')} &rarr;</a>
<p class="muted" style="font-size:13px;margin:10px 0 0">{t('401(k), 403(b), IRA, index funds, single stocks, PER, PEA, RRSP, TFSA; employer match, fees, inflation and the 2026 limits.', "401(k), 403(b), IRA, fonds indiciels, actions, PER, PEA, REER, CELI ; contrepartie de l'employeur, frais, inflation et plafonds 2026.")}</p>
</aside>
</div></section>""" + SCRIPT
