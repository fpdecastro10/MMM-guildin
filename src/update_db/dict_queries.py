DATASET_DATE = [
    {
        "name": "dataset_2_Week_later_salesmorethan0.csv",
        "header": "name_storeGroup,campaign_storeGroup,name_product,name_retailer,id_union_storeGroup_product,id_storeGroup,id_sku,id_store_retailer,cost_campaign,cpc_campaign,cpm_campaign,ctr_campaign,impressions_campaign,yearweek_campaign,cantidad_de_stores_por_storeGroup,cant_de_prod_por_storeGroup,sales,currency_id,revenue,ISOweek\n",
        "query":
        """
        select

            asignador_store_groups.name as name_storeGroup, 
            asignador_store_groups.campaign as campaign_storeGroup,
            importador_productos.name as name_product,
            importador_retailers.name as name_retailer,

            asignador_store_groups_productos.id as id_union_storeGroup_product,
            asignador_store_groups_productos.store_group_id as id_storeGroup,
            asignador_store_groups_productos.sku_id as id_sku,

            asignador_store_groups_productos_stores.id_store_id as id_store_retailer,

            campaign_group_sku_id.cost as cost_campaign,
            campaign_group_sku_id.cpc as cpc_campaign,
            campaign_group_sku_id.cpm as cpm_campaign,
            campaign_group_sku_id.ctr as ctr_campaign,
            campaign_group_sku_id.impressions as impressions_campaign,
            campaign_group_sku_id.yearweek as yearweek_campaign,

            cantidad_de_stores_por_storeGroup.cantidad_de_stores_por_storeGroup as cantidad_de_stores_por_storeGroup,
            cantidad_de_productos_por_stores.cant_de_prod_por_storeGroup as cant_de_prod_por_storeGroup,

            importador_sales_All.sales,
            importador_sales_All.currency_id,
            importador_sales_All.revenue,
            importador_sales_All.ISOweek

        from

        (SELECT store_group_sku_id,
                yearweek,
                sum(cost) as cost,
                sum(cpc) as cpc,
                sum(cpm) as cpm,
                sum(ctr) as ctr,
                sum(impressions) as impressions
        FROM asignador_store_groups_productos_campaign
        LEFT JOIN campaignUnionsView ON 
            campaignUnionsView.campaign_id = asignador_store_groups_productos_campaign.campaign_id
        WHERE tabla_medio IN ('Facebook Weekly','Google Weekly')
        GROUP BY store_group_sku_id,yearweek)

        AS campaign_group_sku_id

        LEFT JOIN asignador_store_groups_productos ON
            asignador_store_groups_productos.id = campaign_group_sku_id.store_group_sku_id
            
        LEFT JOIN asignador_store_groups_productos_stores ON 
            asignador_store_groups_productos_stores.store_group_sku_id = asignador_store_groups_productos.id
            
        LEFT JOIN 
            (select store_group_id,count(*) as cant_de_prod_por_storeGroup
            from asignador_store_groups_productos
            group by store_group_id
            ) as cantidad_de_productos_por_stores ON cantidad_de_productos_por_stores.store_group_id = asignador_store_groups_productos.store_group_id
        LEFT JOIN
            (
            select store_group_sku_id,count(*) as cantidad_de_stores_por_storeGroup
            from asignador_store_groups_productos_stores
            group by store_group_sku_id
            ) as cantidad_de_stores_por_storeGroup ON cantidad_de_stores_por_storeGroup.store_group_sku_id = asignador_store_groups_productos.id

        INNER JOIN
            importador_sales_All ON 
                importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id AND
                importador_sales_All.sku_id = asignador_store_groups_productos.sku_id AND
                CAST(importador_sales_All.ISOweek AS SIGNED) = CAST(campaign_group_sku_id.yearweek AS SIGNED) + 2

        LEFT JOIN asignador_store_groups
            ON asignador_store_groups_productos.store_group_id = asignador_store_groups.id

        LEFT JOIN importador_productos
            ON asignador_store_groups_productos.sku_id = importador_productos.id

        LEFT JOIN importador_retailers
            ON importador_retailers.id = importador_sales_All.retailer_id
        LEFT JOIN importador_paises
            ON importador_paises.id = importador_sales_All.country_id
        WHERE
        asignador_store_groups_productos.date_from IS NOT NULL
        AND asignador_store_groups_productos.date_to IS NOT NULL
        AND importador_sales_All.sales > 0
        AND importador_paises.country_name = 'USA'

        """
    },
    {
        "name": "dataset_to_detect_performance_of_stores.csv",
        "header": "name_storeGroup,campaign_storeGroup,name_product,id_union_storeGroup_product,id_storeGroup,sku_id,id_store_retailer,id_store,id_retailer,retailer_name,ISOweek,sales\n",
        "query": """
        SELECT 

            asignador_store_groups.`name` as name_storeGroup,
            asignador_store_groups.campaign as campaign_storeGroup,

            importador_productos.name as name_product,
            
            asignador_store_groups_productos.id as id_union_storeGroup_product,
            asignador_store_groups_productos.store_group_id as id_storeGroup,
            asignador_store_groups_productos.sku_id as sku_id,
            
            asignador_store_groups_productos_stores.id_store_id as id_store_retailer,
            
            importador_stores.store_id as id_store,
            importador_stores.retailer_id as id_retailer,
            importador_retailers.name as retailer_name,

            importador_sales_All.ISOweek,
            importador_sales_All.sales
            
        FROM asignador_store_groups_productos
        LEFT JOIN asignador_store_groups_productos_stores
            ON asignador_store_groups_productos.id = asignador_store_groups_productos_stores.store_group_sku_id
        LEFT JOIN asignador_store_groups
            ON asignador_store_groups.id = asignador_store_groups_productos.store_group_id 
        LEFT JOIN importador_stores
            ON importador_stores.id = asignador_store_groups_productos_stores.id_store_id
        LEFT JOIN importador_productos
            ON asignador_store_groups_productos.sku_id = importador_productos.id
        LEFT JOIN importador_sales_All
                ON importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id AND
                asignador_store_groups_productos.sku_id = importador_sales_All.sku_id
        LEFT JOIN importador_retailers
            ON importador_retailers.id = importador_stores.retailer_id
        LEFT JOIN importador_paises
                ON importador_paises.id = importador_sales_All.country_id
        WHERE 
            asignador_store_groups_productos.date_from IS NOT NULL AND
            asignador_store_groups_productos.date_to IS NOT NULL AND
            importador_sales_All.ISOweek >= 202200 AND
            importador_paises.country_name = 'USA'
    """
    },
#     {
#         "name": "datasetCampignSales.csv",
#         "header": "yearweek,campaign_id,campaign_name,currency,impressions,ctr,cpc,cpm,cost,media,clicks,cost_convertion,store_group_id,tabla_medio,name_storeGroup,campaign,ISOweek,sales\n",
#         "query": """
#         SELECT
#             campaignUnionsView.yearweek,
#             campaignUnionsView.campaign_id,
#             campaignUnionsView.campaign_name,
#             campaignUnionsView.currency,
#             campaignUnionsView.impressions,
#             campaignUnionsView.ctr,
#             campaignUnionsView.cpc,
#             campaignUnionsView.cpm,
#             campaignUnionsView.cost,
#             campaignUnionsView.media,
#             campaignUnionsView.clicks,
#             campaignUnionsView.cost_convertion,

#             storeGroup_campaignId.store_group_id,
#             storeGroup_campaignId.tabla_medio,
#             storeGroup_campaignId.name,
#             storeGroup_campaignId.campaign,

#             storeGroupISOweekSales.ISOweek,
#             storeGroupISOweekSales.sales

#         from campaignUnionsView
#         inner join (
#             select
#                 asignador_store_groups.id as store_group_id,
#                 asignador_store_groups.name,
#                 asignador_store_groups.campaign,
#                 asignador_store_groups_productos_campaign.campaign_id,
#                 asignador_store_groups_productos_campaign.tabla_medio
#             from asignador_store_groups_productos_campaign
#             left join asignador_store_groups_productos on
#                 asignador_store_groups_productos_campaign.store_group_sku_id = asignador_store_groups_productos.id
#             left join asignador_store_groups
#                 on asignador_store_groups.id = asignador_store_groups_productos.store_group_id
#             where
#                 asignador_store_groups_productos.date_from is not null
#                 and asignador_store_groups_productos.date_to is not null
#                 and asignador_store_groups_productos_campaign.tabla_medio in ("Facebook Weekly", "Google Weekly")
#             group by
#                 asignador_store_groups.id,
#                 asignador_store_groups.name,
#                 asignador_store_groups.campaign,
#                 asignador_store_groups_productos_campaign.campaign_id,
#                 asignador_store_groups_productos_campaign.tabla_medio
#         ) as storeGroup_campaignId
#         on storeGroup_campaignId.campaign_id = campaignUnionsView.campaign_id
#         right join (
#             select
#                 asignador_store_groups_productos.store_group_id,
#                 importador_sales_All.ISOweek,
#                 sum(importador_sales_All.sales) as sales
#             from asignador_store_groups_productos
#             left join asignador_store_groups_productos_stores
#             on asignador_store_groups_productos.id = asignador_store_groups_productos_stores.store_group_sku_id
#             left join importador_sales_All
#                 on importador_sales_All.sku_id = asignador_store_groups_productos.sku_id
#                 and importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id
#             left join importador_paises
#                 ON importador_paises.id = importador_sales_All.country_id
#             where asignador_store_groups_productos.date_from is not null
#                 and asignador_store_groups_productos.date_to is not null
#                 and importador_paises.country_name = 'USA'
#             group by asignador_store_groups_productos.store_group_id,
#                 importador_sales_All.ISOweek
#         ) as storeGroupISOweekSales
#             on storeGroupISOweekSales.store_group_id = storeGroup_campaignId.store_group_id
#             and CAST(storeGroupISOweekSales.ISOweek AS SIGNED) = CAST(campaignUnionsView.yearweek AS SIGNED) + 1
#         where storeGroup_campaignId.store_group_id is not null
# """
#     },
    {
        "name": "dataset_1_Week_later_salesmorethan0.csv",
        "header": "name_storeGroup,campaign_storeGroup,name_product,name_retailer,id_union_storeGroup_product,id_storeGroup,id_sku,id_store_retailer,cost_campaign,cpc_campaign,cpm_campaign,ctr_campaign,impressions_campaign,yearweek_campaign,cantidad_de_stores_por_storeGroup,cant_de_prod_por_storeGroup,sales,currency_id,revenue,ISOweek\n",
        "query":"""
        select 
            asignador_store_groups.name as name_storeGroup,
            asignador_store_groups.campaign as campaign_storeGroup,
            importador_productos.name as name_product,
            importador_retailers.name as name_retailer,

            asignador_store_groups_productos.id as id_union_storeGroup_product,
            asignador_store_groups_productos.store_group_id as id_storeGroup,
            asignador_store_groups_productos.sku_id as id_sku,
            
            asignador_store_groups_productos_stores.id_store_id as id_store_retailer,
            
            campaign_group_sku_id.cost as cost_campaign,
            campaign_group_sku_id.cpc as cpc_campaign,
            campaign_group_sku_id.cpm as cpm_campaign,
            campaign_group_sku_id.ctr as ctr_campaign,
            campaign_group_sku_id.impressions as impressions_campaign,
            campaign_group_sku_id.yearweek as yearweek_campaign,
            
            cantidad_de_stores_por_storeGroup.cantidad_de_stores_por_storeGroup as cantidad_de_stores_por_storeGroup,
            cantidad_de_productos_por_stores.cant_de_prod_por_storeGroup as cant_de_prod_por_storeGroup,

            importador_sales_All.sales,
            importador_sales_All.currency_id,
            importador_sales_All.revenue,
            importador_sales_All.ISOweek

        from

        (SELECT store_group_sku_id,
                yearweek,
                sum(cost) as cost,
                sum(cpc) as cpc,
                sum(cpm) as cpm,
                sum(ctr) as ctr,
                sum(impressions) as impressions
        FROM asignador_store_groups_productos_campaign
        LEFT JOIN campaignUnionsView ON 
            campaignUnionsView.campaign_id = asignador_store_groups_productos_campaign.campaign_id
        WHERE tabla_medio IN ('Facebook Weekly','Google Weekly')
        GROUP BY store_group_sku_id,yearweek)

        AS campaign_group_sku_id

        LEFT JOIN asignador_store_groups_productos ON
            asignador_store_groups_productos.id = campaign_group_sku_id.store_group_sku_id
            
        LEFT JOIN asignador_store_groups_productos_stores ON 
            asignador_store_groups_productos_stores.store_group_sku_id = asignador_store_groups_productos.id
            
        LEFT JOIN 
            (select store_group_id,count(*) as cant_de_prod_por_storeGroup
            from asignador_store_groups_productos
            group by store_group_id
            ) as cantidad_de_productos_por_stores ON cantidad_de_productos_por_stores.store_group_id = asignador_store_groups_productos.store_group_id
        LEFT JOIN
            (
            select store_group_sku_id,count(*) as cantidad_de_stores_por_storeGroup
            from asignador_store_groups_productos_stores
            group by store_group_sku_id
            ) as cantidad_de_stores_por_storeGroup ON cantidad_de_stores_por_storeGroup.store_group_sku_id = asignador_store_groups_productos.id

        INNER JOIN
            importador_sales_All ON 
                importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id AND
                importador_sales_All.sku_id = asignador_store_groups_productos.sku_id AND
                CAST(importador_sales_All.ISOweek AS SIGNED) = CAST(campaign_group_sku_id.yearweek AS SIGNED) + 1

        LEFT JOIN asignador_store_groups
            ON asignador_store_groups_productos.store_group_id = asignador_store_groups.id

        LEFT JOIN importador_productos
            ON asignador_store_groups_productos.sku_id = importador_productos.id

        LEFT JOIN importador_retailers
            ON importador_retailers.id = importador_sales_All.retailer_id
        LEFT JOIN importador_paises
            ON importador_paises.id = importador_sales_All.country_id
        WHERE
        asignador_store_groups_productos.date_from IS NOT NULL
        AND asignador_store_groups_productos.date_to IS NOT NULL
        AND importador_sales_All.sales > 0
        AND importador_paises.country_name = 'USA'
    """
    },
    {
        "name": "datasetCampignSales.csv",
        "header": "yearweek,campaign_id,campaign_name,currency,impressions,ctr,cpc,cpm,cost,media,clicks,cost_convertion,store_group_id,tabla_medio,name_storeGroup,campaign,ISOweek,sales\n",
        "query": """
        SELECT
            campaignUnionsView.yearweek,
            campaignUnionsView.campaign_id,
            campaignUnionsView.campaign_name,
            campaignUnionsView.currency,
            campaignUnionsView.impressions,
            campaignUnionsView.ctr,
            campaignUnionsView.cpc,
            campaignUnionsView.cpm,
            campaignUnionsView.cost,
            campaignUnionsView.media,
            campaignUnionsView.clicks,
            campaignUnionsView.cost_convertion,
            
            storeGroup_campaignId.store_group_id,
            storeGroup_campaignId.tabla_medio,
            storeGroup_campaignId.name,
            storeGroup_campaignId.campaign,
            
            storeGroupISOweekSales.ISOweek,
            storeGroupISOweekSales.sales

        from campaignUnionsView
        inner join (
            select 
                asignador_store_groups.id as store_group_id,
                asignador_store_groups.name,
                asignador_store_groups.campaign,
                asignador_store_groups_productos_campaign.campaign_id,
                asignador_store_groups_productos_campaign.tabla_medio
            from asignador_store_groups_productos_campaign
            left join asignador_store_groups_productos on
                asignador_store_groups_productos_campaign.store_group_sku_id = asignador_store_groups_productos.id
            left join asignador_store_groups
                on asignador_store_groups.id = asignador_store_groups_productos.store_group_id
            where asignador_store_groups_productos.date_from is not null
                and asignador_store_groups_productos.date_to is not null
                and asignador_store_groups_productos_campaign.tabla_medio in ("Facebook Weekly", "Google Weekly")
            group by asignador_store_groups.id,
                asignador_store_groups.name,
                asignador_store_groups.campaign,
                asignador_store_groups_productos_campaign.campaign_id,
                asignador_store_groups_productos_campaign.tabla_medio
        ) as storeGroup_campaignId
        on storeGroup_campaignId.campaign_id = campaignUnionsView.campaign_id
        inner join (
        select 
            asignador_store_groups_productos.store_group_id,
            importador_sales_All.ISOweek,
            sum(importador_sales_All.sales) as sales
        from asignador_store_groups_productos
        left join asignador_store_groups_productos_stores
        on asignador_store_groups_productos.id = asignador_store_groups_productos_stores.store_group_sku_id
        left join importador_sales_All
        on importador_sales_All.sku_id = asignador_store_groups_productos.sku_id
        and importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id
        left join importador_paises
            ON importador_paises.id = importador_sales_All.country_id
        where asignador_store_groups_productos.date_from is not null
            and asignador_store_groups_productos.date_to is not null
            and importador_paises.country_name = 'USA'
        group by asignador_store_groups_productos.store_group_id,
            importador_sales_All.ISOweek
        ) as storeGroupISOweekSales
            on storeGroupISOweekSales.store_group_id = storeGroup_campaignId.store_group_id
            and CAST(storeGroupISOweekSales.ISOweek AS SIGNED) = CAST(campaignUnionsView.yearweek AS SIGNED) + 1
        """
    },
    {
        "name": "datasetCampignSalesNew.csv",
        "header": "store_group_id,ISOweek,sales,name,campaign,tabla_medio,yearweek,cost_campaign\n",
        "query": """
        select
            sales_store_group.store_group_id,
            sales_store_group.ISOweek,
            sales_store_group.sales,
            
            asignador_store_groups.name,
            asignador_store_groups.campaign,
            
            campaign_table.tabla_medio,
            campaign_table.yearweek,
            campaign_table.cost_campaign
            
        FROM(
            SELECT 
                asignador_store_groups_productos.store_group_id,
                importador_sales_All.ISOweek,
                sum(importador_sales_All.sales) as sales
            FROM asignador_store_groups_productos
            LEFT JOIN asignador_store_groups_productos_stores
                ON asignador_store_groups_productos.id = asignador_store_groups_productos_stores.store_group_sku_id
            LEFT JOIN importador_sales_All
                ON importador_sales_All.sku_id = asignador_store_groups_productos.sku_id
                AND importador_sales_All.id_store_id = asignador_store_groups_productos_stores.id_store_id
            LEFT JOIN importador_paises
                ON importador_paises.id = importador_sales_All.country_id
            WHERE asignador_store_groups_productos.date_from IS NOT NULL
                AND asignador_store_groups_productos.date_to IS NOT NULL
                AND importador_paises.country_name = 'USA'
            GROUP BY 
                asignador_store_groups_productos.store_group_id,
                importador_sales_All.ISOweek
        ) as sales_store_group
        LEFT JOIN asignador_store_groups
            ON asignador_store_groups.id = sales_store_group.store_group_id
        LEFT JOIN(
            SELECT 
                asignador_store_groups_productos.store_group_id,
                asignador_store_groups_productos_campaign.tabla_medio,
                campaignUnionsView.yearweek,
                campaignUnionsView.campaign_id,
                avg(campaignUnionsView.cost) as cost_campaign
            FROM asignador_store_groups_productos_campaign
            INNER JOIN campaignUnionsView
                ON asignador_store_groups_productos_campaign.campaign_id = campaignUnionsView.campaign_id
            LEFT JOIN asignador_store_groups_productos
                ON asignador_store_groups_productos_campaign.store_group_sku_id = asignador_store_groups_productos.id
            GROUP BY 
                asignador_store_groups_productos.store_group_id,
                asignador_store_groups_productos_campaign.tabla_medio,
                campaignUnionsView.yearweek,
                campaignUnionsView.campaign_id
        ) AS campaign_table
        -- ON CAST(sales_store_group.ISOweek AS SIGNED) = CAST(campaign_table.yearweek AS SIGNED) + 2
            ON 
            /*
            Lo que hacemos aca es hacer el match normal entre con dos semanas de delay, y tambien contemplar el caso en que se cambie de año
            */
            (CASE
                WHEN 
                -- ISOweek : ventas, yearweek : costo campaña
                    (campaign_table.yearweek  % 100) % 52 = 0
                THEN
                    CASE 
                        -- Comparamos si existe desfasaje de una semana y 
                        WHEN floor(campaign_table.yearweek / 100) = floor(sales_store_group.ISOweek / 100) - 1
                            AND (sales_store_group.ISOweek % 100) % 52 = floor(campaign_table.yearweek % 100) % 52 + 1
                        THEN
                            1
                        ELSE
                            0
                    END
                ELSE
                    CASE 
                        -- Comparamos si existe desfasaje de una semana y 
                        WHEN 
                            floor(campaign_table.yearweek / 100) = floor(sales_store_group.ISOweek / 100)
                            AND (sales_store_group.ISOweek % 100) = floor(campaign_table.yearweek % 100) + 1
                        THEN
                            1
                        ELSE
                            0
                    END
            END
            ) = 1
            AND 
            campaign_table.store_group_id = sales_store_group.store_group_id

"""
    }

]