import sys
import json


def get_mensualite_credit(capital, dico):
    t = (dico['credit']['taux'] / 100) / 12
    n = dico['credit']['années'] * 12
    mensualite_hors_assurance = capital * t / (1 - (1 + t) ** -n)
    mensualite_totale = mensualite_hors_assurance + dico['credit']["assu_par_mois"]
    return round(mensualite_totale, 2)


if __name__ == '__main__':
    dico = json.load(open(sys.argv[1]))

    salaire_marine_mois_net = dico['marine']['salaire_mois_net']
    if dico['marine'].get('80', False):
        salaire_marine_mois_net_100 = round((salaire_marine_mois_net / 80) * 100)
    marine_apport = dico['marine']['apport']
    marine_nature = dico['marine']['nature_mois']
    salaire_marine_tout_avantage = salaire_marine_mois_net_100 + marine_nature
    franck_apport = dico['franck']['apport']

    apport = franck_apport + marine_apport

    maison_ref_prix = dico['maison_ref']['prix_annonce']
    maison_ref_cout = maison_ref_prix
    maison_reelle_prix = dico['maison_reelle']['prix_maison']

    emprunt = maison_ref_cout - apport

    mensualite_credit = get_mensualite_credit(emprunt, dico)
    mensuel_foyer_hors_credit = dico['foyer']['cout_hors_credit']
    mensuel_foyer = mensuel_foyer_hors_credit + mensualite_credit

    if dico['marine'].get('80', False):
        print(f"Salaire Marine 80 % / mois net : {dico['marine']['salaire_mois_net']} €" )
    print(f'Salaire Marine 100 % / mois net : {salaire_marine_mois_net_100} €' )
    print(f'Salaire Marine 100 % / mois net - Avec anvantages : {salaire_marine_tout_avantage} €' )
    print(f'Apport Marine : {marine_apport} €' )
    print(f'Apport Franck : {franck_apport} €' )
    print(f'Apport Total : {apport} €' )
    print(f'Maison de référence, prix annonce : {maison_ref_prix} €' )
    print(f'Maison de référence, après négo, + frais notaires : {maison_ref_cout} €' )
    print(f'Maison réelle achat : {maison_reelle_prix} €' )
    print(f'Montant emprunté : {emprunt} €' )
    print(f'Mensualité crédit : {mensualite_credit} €' )
    print(f'Mensuel foyer (hors credit) : {mensuel_foyer_hors_credit} €' )
    print(f'Mensuel foyer total : {mensuel_foyer} €' )


    for contrib_foyer_marine in dico['marine']['contribs_cc']:
        print('*********')
        contrib_foyer_marine_tot = contrib_foyer_marine + dico['marine']['nature_mois']
        contrib_foyer_marine_pct = round(contrib_foyer_marine_tot / mensuel_foyer * 100, 2) / 100
        contrib_marine_maison = round(marine_apport + contrib_foyer_marine_pct * (maison_ref_prix-apport))
        contrib_franck_maison = maison_ref_prix - contrib_marine_maison
        contrib_marine_maison_pct = round(contrib_marine_maison / maison_ref_prix, 2)
        contrib_franck_maison_pct = round(1 - contrib_marine_maison_pct, 2)
        contrib_marine_maison_reelle = contrib_marine_maison
        contrib_franck_maison_reelle = maison_reelle_prix - contrib_marine_maison_reelle
        contrib_marine_maison_reelle_pct = round(contrib_marine_maison_reelle / maison_reelle_prix, 2)
        contrib_franck_maison_reelle_pct = round(1 - contrib_marine_maison_reelle_pct, 2)
        print(f"Contrib mensuelle Marine : {contrib_foyer_marine_tot} ({contrib_foyer_marine} + {dico['marine']['nature_mois']}) € ({contrib_foyer_marine_pct*100} %)")
        print(f'Budget investi au bout de 25 ans (maison ref) : ')
        print(f'  - Marine : {contrib_marine_maison} € ({contrib_marine_maison_pct * 100} %)')
        print(f'  - Franck : {contrib_franck_maison} € ({contrib_franck_maison_pct * 100} %)')
        print(f'Budget investi au bout de 25 ans (reelle maison) : ')
        print(f'  - Marine : {contrib_marine_maison_reelle} € ({round(contrib_marine_maison_reelle_pct * 100, 2)} %)')
        print(f'  - Franck : {contrib_franck_maison_reelle} € ({round(contrib_franck_maison_reelle_pct * 100, 2)} %)')
