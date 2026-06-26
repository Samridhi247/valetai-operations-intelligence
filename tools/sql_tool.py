import sqlite3
import pandas as pd
from langchain.tools import tool

@tool
def run_sql_query(query: str) -> str:
    """
    Executes a SQL SELECT query on the ValetAI Operations Intelligence database
    and returns the query result.

    ============================================================
    DATABASE OVERVIEW
    ============================================================

    This database contains operational data for ValetAI, an operations
    intelligence platform that monitors waste collection performance across
    residential properties.

    The database consists of TWO TABLES.

   ------------------------------------------------------------
    TABLE 1 : property_metrics
    ------------------------------------------------------------

    This table contains ONE ROW PER PROPERTY.

    PURPOSE:

    This is the PRIMARY business analytics table.

    It stores the OFFICIAL pre-computed performance KPIs for every property.

    Whenever a user asks about overall property performance,
    management reports, rankings, dashboards, summaries, or business metrics,
    ALWAYS use this table.

    DO NOT recalculate these metrics from waste_logs.

    Columns:

    property_name              TEXT
    property_id                TEXT
    total_collections          INTEGER
    total_missed_pickups       INTEGER
    total_bags_collected       INTEGER
    avg_completion_minutes     REAL
    missed_pickup_rate         REAL

    Always use this table for:

    • Property performance
    • Comparing properties
    • Executive summaries
    • Business reports
    • Highest / Lowest values
    • Rankings
    • Best / Worst properties
    • Top N / Bottom N properties
    • Overall analytics
    • Total collections
    • Total missed pickups
    • Total bags collected
    • Missed pickup rate
    • Average completion time

    IMPORTANT

    The following are OFFICIAL business KPIs and MUST be read directly from this table.

    • total_collections
    • total_missed_pickups
    • total_bags_collected
    • avg_completion_minutes
    • missed_pickup_rate

    Never recompute these metrics from waste_logs.


    ------------------------------------------------------------
    TABLE 2 : waste_logs
    ------------------------------------------------------------

    This table contains ONE ROW PER COLLECTION EVENT.

    PURPOSE:

    This table stores RAW operational collection events.

    Use this table only when the user wants event-level,
    historical, route, collector, or date-based analysis.

    This table is NOT the source of official property KPIs.

    Columns:

    collection_id          TEXT
    property_id            TEXT
    property_name          TEXT
    collection_date        TEXT
    route_id               TEXT
    bags_collected         INTEGER
    missed_pickups         INTEGER
    completion_time        REAL
    collector_id           TEXT
    region                 TEXT

    Use this table ONLY when the user asks about:

    • Individual collection events
    • Historical records
    • Route analysis
    • Collector performance
    • Region analysis
    • Daily operations
    • Collection history
    • Date filtering
    • Frequency analysis
    • Time-based analysis

    IMPORTANT

    Use waste_logs only for RAW operational events.

    Do NOT use waste_logs to calculate or estimate:

    • average completion time of a property
    • missed pickup rate
    • total collections
    • total bags collected
    • total missed pickups
    • property rankings
    • executive summaries
    • business reports

    Those values already exist in property_metrics and should always be retrieved from there.


    ============================================================
    SQL GENERATION RULES
    ============================================================

    1. ONLY generate SELECT statements.

    2. NEVER generate:
       INSERT
       UPDATE
       DELETE
       DROP
       ALTER
       CREATE
       TRUNCATE

    3. NEVER invent table names.

    4. NEVER invent column names.

    5. Use ONLY the columns listed above.

    6. Use the correct table depending on the user's question.

    ============================================================
    BUSINESS SEMANTICS
    ============================================================

    Interpret common business language as follows.

    If the user says

    "struggling"
    "poor performing"
    "underperforming"
    "needs attention"
    "problematic"
    "worst property"
    "least efficient"

    this means

    HIGHER

    - total_missed_pickups
    - missed_pickup_rate
    - avg_completion_minutes

    These should generally be ordered DESC.

    ------------------------------------------------------------

    If the user says

    "best"
    "top performing"
    "most efficient"
    "highest performing"

    this means

    LOWER

    - total_missed_pickups
    - missed_pickup_rate
    - avg_completion_minutes

    and

    HIGHER

    - total_collections
    - total_bags_collected

    Use business judgement.

    ------------------------------------------------------------

    If the user asks

    "Which property is struggling the most?"

    prefer

    ORDER BY total_missed_pickups DESC

    unless another metric is explicitly requested.

    ------------------------------------------------------------

    If the user asks

    "Why?"

    include the metrics responsible for the ranking.

    Example

    Property Name

    Property ID

    Total Missed Pickups

    Missed Pickup Rate

    Average Completion Time

    -----------------------------------------------------
    If the user asks

    - compare
    - versus
    - vs
    - difference between

    always return

    property_name
    property_id
    total_collections
    total_missed_pickups
    missed_pickup_rate
    avg_completion_minutes

    for ALL requested properties.

    ============================================================
    PROPERTY QUESTIONS
    ============================================================

    If the user asks:

    • highest property
    • lowest property
    • best property
    • worst property
    • compare properties
    • property performance
    • top properties

    ALWAYS use

        property_metrics

    IMPORTANT:

    For property-level performance metrics, ALWAYS use property_metrics.

    The following metrics MUST come from property_metrics:

    - avg_completion_minutes
    - total_collections
    - total_missed_pickups
    - total_bags_collected
    - missed_pickup_rate

    DO NOT calculate these again from waste_logs.

    DO NOT use AVG(completion_time) for property performance questions.

    The property_metrics table already contains the official aggregated business metrics.

    and ALWAYS return

    property_id
    property_name

    along with the requested metric.

    Example:

    SELECT property_id,
           property_name,
           total_missed_pickups
    FROM property_metrics
    ORDER BY total_missed_pickups DESC
    LIMIT 1;


    ============================================================
    COLLECTION QUESTIONS
    ============================================================

    If the user asks about

    • routes
    • collectors
    • regions
    • dates
    • collection events
    • individual collection records
    • daily operations
    • event history

    ALWAYS use

    waste_logs

    IMPORTANT:

    Use waste_logs ONLY for individual collection records.

    DO NOT use waste_logs for overall property performance.

    If the user asks about

    - average completion time of a property
    - total collections
    - total missed pickups
    - missed pickup rate
    - bags collected

    ALWAYS use property_metrics.


    ============================================================
    AGGREGATION RULES
    ============================================================

    If SUM(), AVG(), MIN(), MAX(), COUNT() are used together with
    non aggregated columns,

    ALWAYS use GROUP BY whenever SQL requires it.

    Never return invalid SQL.


    ============================================================
    TOP / BOTTOM QUESTIONS
    ============================================================

    For questions like

    highest
    lowest
    top
    bottom
    best
    worst

    ALWAYS use

    ORDER BY

    together with

    LIMIT


    Example

    ORDER BY total_missed_pickups DESC
    LIMIT 5


    ============================================================
    FREQUENCY QUESTIONS
    ============================================================

    If the user asks

    • occurs most often
    • occurs most frequently
    • appears the most
    • most common value
    • mode
    • frequency
    • repeated most

    DO NOT use MIN() or MAX().

    Instead use

    GROUP BY

    COUNT(*)

    ORDER BY COUNT(*) DESC

    Example

    SELECT
        missed_pickups,
        COUNT(*) AS frequency
    FROM waste_logs
    GROUP BY missed_pickups
    ORDER BY frequency DESC
    LIMIT 1;


    ============================================================
    MIN/MAX OCCURRENCE QUESTIONS
    ============================================================

    If the user asks

    "How many times does the minimum value occur?"

    First find the minimum value.

    Then count its occurrences.

    Example

    SELECT
        missed_pickups,
        COUNT(*) AS frequency
    FROM waste_logs
    WHERE missed_pickups =
        (
            SELECT MIN(missed_pickups)
            FROM waste_logs
        )
    GROUP BY missed_pickups;


    ============================================================
    DATE QUESTIONS
    ============================================================

    Questions involving

    today
    yesterday
    this week
    this month
    between dates

    MUST use

    collection_date

    from

    waste_logs.


    ============================================================
    RANKING QUESTIONS
    ============================================================

    Questions like

    Top 5
    Bottom 10
    Rank
    Highest
    Lowest

    MUST use

    ORDER BY

    with

    LIMIT.


    ============================================================
    COMPARISON QUESTIONS
    ============================================================

    Questions comparing two or more properties

    MUST return all requested properties in ONE query.

    Do not execute multiple queries unnecessarily.


    ============================================================
    SQL ERROR HANDLING
    ============================================================

    If a SQL query fails,

    READ the error.

    Understand why it failed.

    Generate a corrected query.

    Never repeat the exact same invalid query.

    Never guess nonexistent columns.


    ============================================================
    RESPONSE RULES
    ============================================================

    After executing the SQL query,

    Explain the result in clear business language.

    Mention

    • property name
    • property id
    • metric
    • ranking

    whenever applicable.

    If no rows are returned,

    clearly say

    "No matching records were found."

    Never fabricate values.

    Never hallucinate columns.

    Never hallucinate tables.

    Base every answer ONLY on the SQL query results.

    """
    try:
        conn = sqlite3.connect("data/valetai.db")
        result = pd.read_sql_query(query, conn)
        print("========== GENERATED SQL ==========")
        print(query)
        conn.close()
        print("========== RAW SQL RESULT ==========")
        print(result)
        return result.to_string(index=False)
        # return result.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {str(e)}"


# @tool
# def run_sql_query(query: str) -> str:
#     """
#     Runs a SQL query against the ValetAI database and returns the results.
#     The database has two tables:
#     - property_metrics (one row per property, pre-aggregated totals - columns: property_name,
#       total_collections, total_missed_pickups, total_bags_collected, avg_completion_minutes,
#       missed_pickup_rate). USE THIS TABLE for any question comparing properties overall,
#       asking for "best", "worst", "highest", "lowest", "total", or "rate" - these refer to
#       property-level totals, not individual collection events.
#     - waste_logs (one row per individual collection event - columns: collection_id, property_id,
#       property_name, collection_date, route_id, bags_collected, missed_pickups, completion_time,
#       collector_id, region). Only use this for questions about specific dates, routes, or
#       individual collection events, not for property-level comparisons.
#     Only use SELECT statements. Always use exact column names listed above.
#     When asked for a minimum, maximum, best, or worst value, always also select the
#     corresponding property_name or property_id in the same query - never return an
#     aggregate value alone without its identifying property.
#     """
#     try:
#         conn = sqlite3.connect("data/valetai.db")
#         result = pd.read_sql(query, conn)
#         conn.close()
#         return result.to_string(index=False)
#     except Exception as e:
#         return f"SQL Error: {str(e)}"