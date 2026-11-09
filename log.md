DAY 07 – PURCHASE ORDER MCP ARCHITECTURE

                 USER / AI AGENT
                        |
                        |
                   MCP REQUEST
                        |
                        v
                 MCP SERVER
                 (server.py)
                        |
                        |
              +---------+---------+
              |                   |
              v                   v
       SEARCH TOOL           FILTER TOOL
   search_purchase_orders  filter_purchase_orders
              |                   |
              +---------+---------+
                        |
                        v
              PURCHASE ORDERS JSON
              (purchase_orders.json)
                        |
                        v
                PO RECORDS RETURNED
                        |
                        v
                   MCP SERVER
                        |
                        v
                 USER / AI AGENT
                  (Results)
