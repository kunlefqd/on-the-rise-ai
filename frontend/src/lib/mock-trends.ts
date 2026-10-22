/**
 * MOCK DATA ONLY — not live YouTube Data API results.
 * Replace via getTrendSummaries() / getTrendDetail() when the pipeline is ready.
 */

import type { TrendDetail, TrendSummary } from "./types";

/** Demo snapshot timestamp shown across the dashboard. */
export const MOCK_LAST_UPDATED = "2026-07-24T13:00:00Z";

export const MOCK_TREND_SUMMARIES: TrendSummary[] = [
  {
    trend_name: "Pistachio",
    category: "flavour",
    trend_score: 88,
    growth_24h: 18,
    growth_7d: 142,
    confidence: "high",
    confidence_score: 91,
    supporting_video_count: 42,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Matcha",
    category: "flavour",
    trend_score: 84,
    growth_24h: 12,
    growth_7d: 96,
    confidence: "high",
    confidence_score: 87,
    supporting_video_count: 38,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Hot Honey",
    category: "flavour",
    trend_score: 81,
    growth_24h: 22,
    growth_7d: 168,
    confidence: "high",
    confidence_score: 85,
    supporting_video_count: 31,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Ube",
    category: "flavour",
    trend_score: 76,
    growth_24h: 15,
    growth_7d: 118,
    confidence: "medium",
    confidence_score: 74,
    supporting_video_count: 24,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Black Sesame",
    category: "ingredient",
    trend_score: 73,
    growth_24h: 9,
    growth_7d: 64,
    confidence: "medium",
    confidence_score: 71,
    supporting_video_count: 19,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Filled Cookie",
    category: "format",
    trend_score: 79,
    growth_24h: 14,
    growth_7d: 88,
    confidence: "high",
    confidence_score: 82,
    supporting_video_count: 29,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Croissant",
    category: "format",
    trend_score: 71,
    growth_24h: 4,
    growth_7d: 21,
    confidence: "medium",
    confidence_score: 68,
    supporting_video_count: 27,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "Sourdough",
    category: "format",
    trend_score: 69,
    growth_24h: 3,
    growth_7d: 12,
    confidence: "medium",
    confidence_score: 66,
    supporting_video_count: 33,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
  {
    trend_name: "High Protein",
    category: "consumer_attribute",
    trend_score: 77,
    growth_24h: 11,
    growth_7d: 73,
    confidence: "high",
    confidence_score: 80,
    supporting_video_count: 26,
    query_region_code: "CA",
    last_updated: MOCK_LAST_UPDATED,
  },
];

export const MOCK_TREND_DETAILS: Record<string, TrendDetail> = {
  Pistachio: {
    trend_name: "Pistachio",
    summary:
      "Pistachio continues to lead bakery search and recipe content in Canada, with strong signal across croissants, cookies, and laminated pastries. Creators emphasize green visual appeal and premium positioning.",
    suggested_rd_opportunity:
      "Pilot a pistachio cream-filled croissant and a pistachio crumble muffin for limited regional launch testing.",
    supporting_videos: [
      {
        title: "Pistachio Cream Croissant Recipe",
        channel_title: "Bake Lab Kitchen",
        video_url: "https://www.youtube.com/watch?v=mock-pistachio-1",
        published_at: "2026-07-18T10:00:00Z",
        view_count: 184200,
        like_count: 9200,
        comment_count: 640,
        evidence_reason:
          "High view velocity and strong engagement on pistachio laminated pastry formats.",
      },
      {
        title: "Why Pistachio Is Everywhere in Bakeries",
        channel_title: "Pastry Trends Weekly",
        video_url: "https://www.youtube.com/watch?v=mock-pistachio-2",
        published_at: "2026-07-20T15:30:00Z",
        view_count: 96200,
        like_count: 5100,
        comment_count: 410,
        evidence_reason:
          "Commentary video citing pistachio as a premium flavour upgrade for retail bakery.",
      },
      {
        title: "Pistachio Cookie Butter Filling",
        channel_title: "Home Bakery Lab",
        video_url: "https://www.youtube.com/watch?v=mock-pistachio-3",
        published_at: "2026-07-22T08:15:00Z",
        view_count: 54100,
        like_count: 2800,
        comment_count: 190,
        evidence_reason:
          "Shows format crossover into filled cookies with measurable comment interest.",
      },
    ],
  },
  Matcha: {
    trend_name: "Matcha",
    summary:
      "Matcha remains a durable flavour with renewed growth in soft cookies, loaf cakes, and cafe-style drinks that spill into bakery SKUs.",
    suggested_rd_opportunity:
      "Develop a matcha white-chocolate soft cookie and a matcha marble loaf for cafe wholesale.",
    supporting_videos: [
      {
        title: "Soft Matcha Cookies That Sell Out",
        channel_title: "Cafe Bake Tips",
        video_url: "https://www.youtube.com/watch?v=mock-matcha-1",
        published_at: "2026-07-17T12:00:00Z",
        view_count: 121400,
        like_count: 7400,
        comment_count: 520,
        evidence_reason:
          "Strong engagement around soft-cookie format with matcha as hero flavour.",
      },
      {
        title: "Matcha Marble Loaf Cake",
        channel_title: "Everyday Pastry",
        video_url: "https://www.youtube.com/watch?v=mock-matcha-2",
        published_at: "2026-07-21T09:45:00Z",
        view_count: 67800,
        like_count: 3100,
        comment_count: 240,
        evidence_reason:
          "Loaf format suggests scalable production and wholesale packaging fit.",
      },
    ],
  },
  "Hot Honey": {
    trend_name: "Hot Honey",
    summary:
      "Hot honey shows the fastest short-term growth, especially on biscuits, fried dough, and sweet-heat glazes for bakery snack formats.",
    suggested_rd_opportunity:
      "Test a hot-honey biscuit and a hot-honey drizzle doughnut as seasonal impulse items.",
    supporting_videos: [
      {
        title: "Hot Honey Biscuits Going Viral",
        channel_title: "Southern Bake Co",
        video_url: "https://www.youtube.com/watch?v=mock-hothoney-1",
        published_at: "2026-07-19T18:00:00Z",
        view_count: 210300,
        like_count: 11200,
        comment_count: 890,
        evidence_reason:
          "Highest 24h growth driver; viewers ask for heat level and bakery SKU versions.",
      },
      {
        title: "Sweet Heat Glaze for Doughnuts",
        channel_title: "Fry & Bake",
        video_url: "https://www.youtube.com/watch?v=mock-hothoney-2",
        published_at: "2026-07-23T11:20:00Z",
        view_count: 45300,
        like_count: 2600,
        comment_count: null,
        evidence_reason:
          "Format extension into glazed doughnuts; comment metric unavailable (stored as null).",
      },
    ],
  },
  Ube: {
    trend_name: "Ube",
    summary:
      "Ube is rising through colourful dessert content and Filipino-inspired bakery adaptations, with solid medium confidence from growing video volume.",
    suggested_rd_opportunity:
      "Explore an ube cheese pandesal and ube swirled cinnamon roll for multicultural market tests.",
    supporting_videos: [
      {
        title: "Ube Cheese Pandesal Soft Rolls",
        channel_title: "Island Kitchen Bake",
        video_url: "https://www.youtube.com/watch?v=mock-ube-1",
        published_at: "2026-07-16T14:00:00Z",
        view_count: 89200,
        like_count: 4800,
        comment_count: 360,
        evidence_reason:
          "High save/like ratio on filled soft-roll format with ube flavour.",
      },
      {
        title: "Ube Cinnamon Roll Swirl",
        channel_title: "Colour Bake Studio",
        video_url: "https://www.youtube.com/watch?v=mock-ube-2",
        published_at: "2026-07-22T16:40:00Z",
        view_count: 38700,
        like_count: 2100,
        comment_count: 150,
        evidence_reason:
          "Visual differentiation supports merchandising and social proof for retail.",
      },
    ],
  },
  "Black Sesame": {
    trend_name: "Black Sesame",
    summary:
      "Black sesame is emerging as a premium nutty ingredient in cookies and soft breads, with moderate confidence due to lower absolute video count.",
    suggested_rd_opportunity:
      "Prototype a black sesame shortbread and black sesame cream bun for premium assortment.",
    supporting_videos: [
      {
        title: "Black Sesame Shortbread Cookies",
        channel_title: "Quiet Baking",
        video_url: "https://www.youtube.com/watch?v=mock-sesame-1",
        published_at: "2026-07-15T10:30:00Z",
        view_count: 51200,
        like_count: 2900,
        comment_count: 180,
        evidence_reason:
          "Ingredient-focused recipes with steady week-over-week view growth.",
      },
      {
        title: "Black Sesame Cream Bun",
        channel_title: "Asian Bakery Notes",
        video_url: "https://www.youtube.com/watch?v=mock-sesame-2",
        published_at: "2026-07-21T13:10:00Z",
        view_count: 27400,
        like_count: 1500,
        comment_count: 95,
        evidence_reason:
          "Supports soft-bun application path for industrial bakery R&D.",
      },
    ],
  },
  "Filled Cookie": {
    trend_name: "Filled Cookie",
    summary:
      "Filled cookies remain a high-engagement format, combining thick soft dough with molten or cream centres across multiple flavour variants.",
    suggested_rd_opportunity:
      "Build a modular filled-cookie platform SKU with rotating seasonal centres.",
    supporting_videos: [
      {
        title: "Molten Filled Cookies Bakery Style",
        channel_title: "Cookie Lab Pro",
        video_url: "https://www.youtube.com/watch?v=mock-filled-1",
        published_at: "2026-07-18T09:00:00Z",
        view_count: 156700,
        like_count: 8700,
        comment_count: 710,
        evidence_reason:
          "Format-level demand with repeated requests for bakery-scale methods.",
      },
      {
        title: "Cream Cheese Filled Soft Cookies",
        channel_title: "Batch Bake Daily",
        video_url: "https://www.youtube.com/watch?v=mock-filled-2",
        published_at: "2026-07-23T07:50:00Z",
        view_count: 62300,
        like_count: 3400,
        comment_count: 260,
        evidence_reason:
          "Shows centre-fill innovation transferable to FGF product lines.",
      },
    ],
  },
  Croissant: {
    trend_name: "Croissant",
    summary:
      "Croissant content is mature but stable, with interest shifting toward filled and hybrid croissant formats rather than plain classics.",
    suggested_rd_opportunity:
      "Prioritize filled croissant variants over plain SKUs for new development capacity.",
    supporting_videos: [
      {
        title: "Filled Croissant Ideas for Bakeries",
        channel_title: "Laminate & Fold",
        video_url: "https://www.youtube.com/watch?v=mock-croissant-1",
        published_at: "2026-07-14T11:00:00Z",
        view_count: 73400,
        like_count: 3900,
        comment_count: 280,
        evidence_reason:
          "Stable baseline signal with clear preference for filled variants.",
      },
    ],
  },
  Sourdough: {
    trend_name: "Sourdough",
    summary:
      "Sourdough remains a foundational format with lower growth but consistent supporting volume, useful as a baseline rather than an emerging spike.",
    suggested_rd_opportunity:
      "Maintain sourdough core quality improvements; pair with trending inclusions rather than new plain SKUs.",
    supporting_videos: [
      {
        title: "Sourdough Inclusion Loaves",
        channel_title: "Wild Yeast Workshop",
        video_url: "https://www.youtube.com/watch?v=mock-sourdough-1",
        published_at: "2026-07-12T08:00:00Z",
        view_count: 44800,
        like_count: 2200,
        comment_count: 170,
        evidence_reason:
          "Steady interest in inclusion loaves rather than plain boules.",
      },
    ],
  },
  "High Protein": {
    trend_name: "High Protein",
    summary:
      "High-protein is a consumer attribute driving bakery reformulation interest, especially in muffins, cookies, and breakfast breads.",
    suggested_rd_opportunity:
      "Evaluate a high-protein muffin and protein cookie with clean-label positioning for retail.",
    supporting_videos: [
      {
        title: "High Protein Bakery Muffins",
        channel_title: "Fuel Bake",
        video_url: "https://www.youtube.com/watch?v=mock-protein-1",
        published_at: "2026-07-19T06:30:00Z",
        view_count: 99800,
        like_count: 5600,
        comment_count: 430,
        evidence_reason:
          "Attribute-led demand with explicit bakery product applications.",
      },
      {
        title: "Protein Cookie Formulation Basics",
        channel_title: "Nutrition Bake Lab",
        video_url: "https://www.youtube.com/watch?v=mock-protein-2",
        published_at: "2026-07-22T19:00:00Z",
        view_count: 41200,
        like_count: 2400,
        comment_count: 210,
        evidence_reason:
          "Formulation discussion indicates R&D relevance beyond consumer recipes.",
      },
    ],
  },
};
