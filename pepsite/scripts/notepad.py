
        qq2 = "CREATE VIEW suppavail_all AS SELECT foo.id, foo.ptmarray, foo.ptmstr, foo.peptide_id, foo.ptmz \
                FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_agg(t2.ptm_id ORDER BY t2.ptm_id) AS ptmarray, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr, \
                array_agg(t3.description order by t3.id) AS ptmz FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                INNER JOIN pepsite_ptm t3 ON ( t3.id = t2.ptm_id ) \
                GROUP BY t1.id, t1.peptide_id, t1.peptide_id) AS foo \
                "
        qq3 = "CREATE VIEW prot_ides AS \
                SELECT t1.id as p2p_id, t1.protein_id, t1.posnarray, t1.posnstr, t2.*, t4.description AS protein_description, t4.prot_id AS uniprot_code FROM found_possies t1 \
                INNER JOIN augmented_ides t2 ON \
                ( t2.peptide_id = t1.peptide_id ) \
                INNER JOIN pepsite_experiment_proteins t3 ON \
                ( t3.experiment_id = t2.experiment_id ) \
                INNER JOIN pepsite_protein t4 \
                ON ( t4.id = t1.protein_id ) \
                WHERE t1.protein_id = t3.protein_id \
                "
