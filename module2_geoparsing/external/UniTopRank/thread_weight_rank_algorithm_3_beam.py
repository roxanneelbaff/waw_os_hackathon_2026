

import os
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from functools import lru_cache

try:
    from rapidfuzz.distance import Levenshtein
except ImportError:
    class _LevenshteinFallback:
        @staticmethod
        def distance(a, b):
            a = a or ""
            b = b or ""
            n, m = len(a), len(b)
            if n == 0:
                return m
            if m == 0:
                return n
            dp = list(range(m + 1))
            for i in range(1, n + 1):
                prev = dp[0]
                dp[0] = i
                for j in range(1, m + 1):
                    tmp = dp[j]
                    cost = 0 if a[i - 1] == b[j - 1] else 1
                    dp[j] = min(
                        dp[j] + 1,
                        dp[j - 1] + 1,
                        prev + cost,
                    )
                    prev = tmp
            return dp[m]

    Levenshtein = _LevenshteinFallback()

import math


QUICK_THRESHOLD = 0.35    



def compute_population_score(population, max_population=20_000_000, alpha=3.5):
    """
    Convert population to a normalized score in [0,1] using logarithmic scaling.
    Larger populations yield higher scores.
    """

    if population <= 0:
        return 0.0
    raw = math.log1p(population) / math.log1p(max_population)
    return raw ** alpha


def min_fast_distance_to_group(lat, lon, lats, lons):
    """
    Compute the minimum Euclidean distance (in km) between a point and a set of points.
    Used for spatial proximity computation.
    """

    if lats.size == 0:
        return 1e9
    d_lat = (lats - lat)
    d_lon = (lons - lon)
    return (np.hypot(d_lat, d_lon).min()) * 111.0

def best_name_similarity1(norm_top, cand_name, alt):
    """
    Compute normalized Levenshtein similarity between a toponym and its candidates.
    """

    norm = norm_top.lower()
    if norm == cand_name.lower() or norm in (n.lower() for n in alt):
        return 1.0
    distances = [Levenshtein.distance(norm, n.lower()) / max(len(norm), len(n)) for n in [cand_name] + alt]
    best = min(distances)
    return max(0, 1 - best)

def haversine(lat1, lon1, lat2, lon2):
    """
    Compute great-circle (Haversine) distance in kilometers between two coordinates.
    """

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = 6371.0
    return R * c

def get_distance(lat1, lon1, lat2, lon2):
    return simple_distance(lat1, lon1, lat2, lon2)

def simple_distance(lat1, lon1, lat2, lon2):
    """
    Compute approximate planar distance (km) between two coordinates.
    """

    d_deg = ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5
    return d_deg * 111



@lru_cache(maxsize=100_000)
def _hierarchical_score_tuple(t1, t2):
    """
    Compute a hierarchical relationship score between two address tuples.
    Higher values mean closer or parent-child relationships.
    Cached for efficiency.
    """

    if t1 == t2:
        return 1.0
    if abs(len(t1) - len(t2)) == 1:
        shorter, longer = (t1, t2) if len(t1) < len(t2) else (t2, t1)
        if longer[1:] == shorter:
            return 1.0
    if len(t1) == len(t2) and len(t1) >= 2 and t1[1:] == t2[1:]:
        return 1.0
    common = 0
    for a, b in zip(reversed(t1), reversed(t2)):
        if a == b:
            common += 1
        else:
            break
    return common / max(len(t1), len(t2))

def hierarchical_relationship_score_cached(tuple1, tuple2):
    """
    Cached version of hierarchical relationship scoring.
    Ensures symmetric lookup order for cache efficiency.
    """

    return _hierarchical_score_tuple(tuple1, tuple2) if id(tuple1) < id(tuple2) else _hierarchical_score_tuple(tuple2, tuple1)

def hierarchical_relationship_score(addr1, addr2):
    """
    Compare two address strings and compute hierarchical similarity
    based on shared components (country, region, etc.).
    """

    def normalize(addr):
        return [comp.strip().lower() for comp in addr.split(',') if comp.strip()]
    comps1 = normalize(addr1)
    comps2 = normalize(addr2)
    if not comps1 or not comps2:
        return 0.0
    if comps1 == comps2:
        return 1.0
    if abs(len(comps1) - len(comps2)) == 1:
        shorter = comps1 if len(comps1) < len(comps2) else comps2
        longer = comps2 if len(comps2) > len(comps1) else comps1
        if longer[1:] == shorter:
            return 1.0
    if len(comps1) == len(comps2) and comps1[1:] == comps2[1:]:
        return 1.0
    common = 0
    for a, b in zip(reversed(comps1), reversed(comps2)):
        if a == b:
            common += 1
        else:
            break
    max_depth = max(len(comps1), len(comps2))
    return common / max_depth


def compute_textual_proximity_weight(current_indices, other_indices, max_text_distance=500):
    return 1

DEBUG = True

def min_haversine_to_group(lat, lon, lats, lons):
    lat1 = np.radians(lat); lon1 = np.radians(lon)
    lat2 = np.radians(lats); lon2 = np.radians(lons)
    dlat = lat2 - lat1; dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return 6371.0 * c.min()


def _is_child_of_with_gap(child_tuple, parent_tuple, max_skip=1):
    """
    Check if a child address tuple is one level deeper than its parent tuple.
    Allows skipping up to 'max_skip' intermediate levels.
    """

    if not child_tuple or not parent_tuple:
        return False
    if len(child_tuple) <= len(parent_tuple):
        return False
    gap = len(child_tuple) - len(parent_tuple)
    if gap < 1 or gap > (max_skip + 1):
        return False
    return tuple(child_tuple[gap:]) == tuple(parent_tuple)
# -------------------------------------------------------------------------------

def compute_hierarchical_spatial_score(
        candidate,
        top_feature_cache,
        current_toponym,
        toponym_text_indices,
        weight_distance=0.5,
        weight_hierarchical=0.5,
        max_distance=300.0,
        max_text_distance=50000,
        similarity_cache={},
        sp_score_type=0,
        spatial_pair_cache=None,
        debug=False):
    """
    Compute the spatial coherence score between a candidate location and
    other toponyms in the same text. Combines:
      - Physical proximity (distance)
      - Hierarchical similarity (shared administrative components)
    Returns a normalized coherence score in [0,1].
    """


    if spatial_pair_cache is None:
        spatial_pair_cache = {}

    pair_scores = []
    text_weights = []
    current_indices = toponym_text_indices.get(current_toponym, [0])

    adjacent_pairs = toponym_text_indices.get('__adjacent__', set())

    # (kept) your temporary pdb statements are disabled to avoid breaking runs
    # FIX: guard your debug breakpoints
    # if False and debug and candidate['address'] == 'Edmonton, Alberta, Canada, North America':
    #     import pdb; pdb.set_trace()
    for other_top, feat in top_feature_cache.items():
        if debug and candidate['address']  == 'Rice Lake, Stoddard County, Missouri, United States, North America' and other_top=='africa':
            import pdb
            pdb.set_trace()

        if other_top == current_toponym.lower():
            continue
        # FIX: guard this one too
        # if  debug and candidate['address'] == 'Edmonton, Alberta, Canada, North America' and other_top.lower() == 'townsville':
        #     import pdb; pdb.set_trace()

        other_indices = toponym_text_indices.get(other_top, [0])
        text_weight_val = compute_textual_proximity_weight(current_indices, other_indices, max_text_distance)
        if text_weight_val == 0:
            continue

        lats_group  = feat['lats']
        lons_group  = feat['lons']
        cand_list   = feat['cand_list']
        addr_tuples = feat['addr_tuples']
        addr_ids    = feat['addr_ids']
        d_min = min_fast_distance_to_group(candidate['lat'], candidate['lon'], lats_group, lons_group)
        if sp_score_type==1:
            physical_score_max = math.exp(-d_min / max_distance)
        elif sp_score_type==2:
            physical_score_max = 1.0 / (1.0 + d_min / max_distance)
        else:
            physical_score_max = max(0.0, 1.0 - d_min / max_distance)
        

        combined_max = 0.0
        ca = candidate['addr_id']
        for idx, other in enumerate(cand_list):
            # FIX: guard this one too
            # if debug and candidate['address'] == 'Edmonton, Alberta, Canada, North America' and other_top.lower() == 'townsville' and cand_list[idx]['address'] =='Townsville Railway Pier, Townsville, Queensland, Australia, Oceania':
            #     import pdb; pdb.set_trace()

            a = ca; b = addr_ids[idx]
            key = (a, b) if a < b else (b, a)
            
            if key in spatial_pair_cache and False:
                hier = spatial_pair_cache[key]
                if debug:
                    print(f"[PAIR][CACHE] {current_toponym}({candidate['address']})  ~  {other_top}({cand_list[idx]['address']})  "
                          f"hier={hier:.4f}")
            else:
                base_hier = hierarchical_relationship_score_cached(candidate['addr_tuple'], addr_tuples[idx])

                adj_lr = (current_toponym.lower(), other_top) in adjacent_pairs
                adj_rl = (other_top, current_toponym.lower()) in adjacent_pairs
                bonus_applied = False
                hier = base_hier
                if (adj_lr and _is_child_of_with_gap(candidate['addr_tuple'], addr_tuples[idx], 1)) or \
                   (adj_rl and _is_child_of_with_gap(addr_tuples[idx], candidate['addr_tuple'], 1)):
                    hier = hier + 2
                    bonus_applied = True

                spatial_pair_cache[key] = hier

                if debug:
                    print(f"[PAIR] {current_toponym}({candidate['address']})  ~  {other_top}({cand_list[idx]['address']})  "
                          f"phys_max={physical_score_max:.4f}  base_hier={base_hier:.4f}  "
                          f"adj_bonus={'Y' if bonus_applied else 'N'}  hier_used={hier:.4f}")

            combined = max(physical_score_max, hier)
            if debug :
                print(f"[PAIR->COMBINED] combined={combined:.4f}  text_w={text_weight_val:.4f}  "
                      f"pair_contrib={combined * text_weight_val:.4f}")

            if combined > combined_max:
                combined_max = combined
            if combined_max == 1:
                break

        pair_scores.append(combined_max * text_weight_val)
        text_weights.append(text_weight_val)

    reward = 0.0
    if len(pair_scores) >= 20:
        cover = sum(s >= 0.5 for s in pair_scores) / len(pair_scores)
        if cover >= 0.8:
            reward = 0

    overall_score = sum(pair_scores) / sum(text_weights) if pair_scores else 0.0
    overall_score = min(1.0, overall_score + reward)

    if debug:
        print(f"[SPATIAL][AGG] topo={current_toponym}  cand={candidate['address']}  "
              f"overall_spatial={overall_score:.4f}")

    return overall_score


# -------------------------------
def normalize_similarity(similarity_score, max_distance=100):
    """
    Normalize a distance-based similarity measure into [0, 1].
    Lower distance → higher normalized similarity.
    """

    return max(0, 1 - (similarity_score / max_distance))

def levenshtein_distance(str1, str2):
    """
    Compute the raw Levenshtein edit distance between two strings.
    Used as a fallback when RapidFuzz similarity is unavailable.
    """

    len_str1 = len(str1); len_str2 = len(str2)
    matrix = np.zeros((len_str1 + 1, len_str2 + 1), dtype=int)
    for i in range(len_str1 + 1):
        matrix[i][0] = i
    for j in range(len_str2 + 1):
        matrix[0][j] = j
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,
                               matrix[i][j - 1] + 1,
                               matrix[i - 1][j - 1] + cost)
    return matrix[len_str1][len_str2]

def compute_name_similarity(toponym, candidate_name, candidate_alt_names=[]):
    """
    Compute normalized name similarity between a toponym and a candidate entry
    using Levenshtein distance. Returns a score in [0,1].
    """

    toponym_lc = toponym.lower()
    all_names = [candidate_name] + candidate_alt_names
    for name in all_names:
        if toponym_lc == name.lower():
            return 1.0
    max_similarity = 0
    for name in all_names:
        dist = levenshtein_distance(toponym_lc, name.lower())
        max_len = max(len(toponym_lc), len(name))
        similarity = normalize_similarity(dist, max_len)
        max_similarity = max(max_similarity, similarity)
    return max_similarity


def normalize_admin_level(level):
    """
    Convert a GeoNames feature code or administrative level into a normalized score.
    Higher administrative levels (countries, regions, capitals) yield higher values.
    """

    if level.startswith("PPL") and not level.startswith("PPLC"):
        return 0.4

    admin_level_map = {
        'CONT': 1.0,
        'PCL': 1.0,
        'PCLI': 1.0,
        'PCLS': 0.9,
        'ADM1': 0.8,
        'ADM1H': 0.7,
        'ADM2': 0.7,
        'ADM2H': 0.6,
        'ADM3': 0.5,
        'ADM3H':0.4,
        'PPLC': 0.8,
        'PPLCH': 0.7,
        'RGN': 0.4,
        'ADM4': 0.4,
        'ADM5': 0.4,
    }
    return admin_level_map.get(level, 0)


# =========================================================
_G_top_feature_cache = None
_G_toponym_text_indices = None
_G_similarity_cache = None
_G_max_text_len = None
_G_addrid_by_addr = None  # <-- NEW

# FIX: accept and store addrid_by_addr
def _init_worker(tfc, tti, sim_cache, max_text_len, addrid_by_addr=None):  # <-- CHANGED SIG
    """
    Initialize global variables for a scoring worker (used for multiprocessing).
    Sets up shared caches and limits thread usage to prevent CPU oversubscription.
    """
    global _G_top_feature_cache, _G_toponym_text_indices, _G_similarity_cache, _G_max_text_len, _G_addrid_by_addr
    _G_top_feature_cache = tfc
    _G_toponym_text_indices = tti
    _G_similarity_cache = sim_cache
    _G_max_text_len = max_text_len
    _G_addrid_by_addr = addrid_by_addr or {}  # <-- NEW
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
    os.environ.setdefault("MKL_NUM_THREADS", "2")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")

def _score_one_toponym(task, debug, spatial_weight, weight_similarity, weight_level, weight_population, distance_thres, sp_score_type, max_population):
    """
    Compute scores for all candidate locations of a single toponym.
    Combines four weighted components:
      - name similarity
      - administrative level
      - population score
      - spatial coherence (hierarchical and geographic consistency)
    Returns: (normalized_toponym, [(candidate, score), ...])
    """

    norm_top, candidates = task
    spatial_pair_cache = {}
    cand_scores = []

    for candidate in candidates:
        name_key = (norm_top, candidate['name'], tuple(candidate.get('alt_names', [])))
        similarity_score = _G_similarity_cache[name_key]
        if similarity_score < 0:
            continue

        admin_level_score = normalize_admin_level(candidate['admin_level'])
        population_score = compute_population_score(candidate['population'], max_population)
        if debug:
            print('*'*50)
            print('candidate', candidate['address'], candidate['admin_level'], candidate['population'])

        # FIX: ensure addr_id is taken from the shared mapping (same id-space as top_feature_cache)
        if 'addr_id' not in candidate:
            addr = candidate['address']
            aid = _G_addrid_by_addr.get(addr)
            if aid is None:
                # allocate consistently into the SAME mapping
                aid = len(_G_addrid_by_addr) + 1
                _G_addrid_by_addr[addr] = aid
            candidate['addr_id'] = aid

        # safety: ensure addr_tuple exists (should have been set in cache builder)
        if 'addr_tuple' not in candidate:
            candidate['addr_tuple'] = tuple(s.strip().lower() for s in candidate['address'].split(',') if s.strip())

        spatial_coherence_score = compute_hierarchical_spatial_score(
            candidate,
            _G_top_feature_cache,
            norm_top,
            _G_toponym_text_indices,
            weight_distance=0.5,
            weight_hierarchical=0.5,
            max_distance=distance_thres,
            sp_score_type=sp_score_type,
            spatial_pair_cache=spatial_pair_cache,
            similarity_cache=_G_similarity_cache,
            max_text_distance=_G_max_text_len,
            debug=debug
        )

        # weight_similarity = 0.3 
        # weight_level =  0.1
        # weight_population = 0.2
        weight_spatial = spatial_weight # 0 

        total_score = (similarity_score * weight_similarity +
                       admin_level_score * weight_level +
                       population_score * weight_population +
                       spatial_coherence_score * weight_spatial)

        cand_scores.append((candidate, total_score))
        if debug:
            print('similarity_score', similarity_score)
            print('admin_level_score', admin_level_score)
            print('population_score', population_score)
            print('spatial_coherence_score', spatial_coherence_score)
            print('total_score', total_score)

    return norm_top, cand_scores


def rank_candidates(toponyms_dict, top_N, toponym_text_indices, debug=False, max_text_len = 50000, not_process=[], spatial_weight=0.4, weight_similarity=0.3, weight_level=0.1, weight_population=0.2, distance_thres=500, sp_score_type=0, max_population=20000000):
    """
    Rank candidate locations for all toponyms in a text or dataset.
    Steps:
      1. Merge duplicate candidates and compute similarity caches.
      2. Build a feature cache for spatial relationships.
      3. Compute scores for each toponym sequentially.
      4. Combine results into Top-N ranked outputs per toponym.

    Returns:
        merged_results: dict {toponym → [(address, lat, lon, score), ...]}
        merged_scores:  dict {toponym → [score1, score2, ...]}
    """

    not_process = set(not_process or [])


    merged_toponyms = {}
    for toponym, candidates in toponyms_dict.items():
        norm_top = toponym.lower()
        merged_toponyms.setdefault(norm_top, []).extend(candidates)


    similarity_cache = {}
    for norm_top, candidates in merged_toponyms.items():
        for candidate in candidates:
            name_key = (norm_top, candidate['name'], tuple(candidate.get('alt_names', [])))
            if name_key not in similarity_cache:
                similarity_score = best_name_similarity1(norm_top, candidate['name'], candidate.get('alt_names', []))
                similarity_cache[name_key] = similarity_score


    addr2id = {}
    def get_addr_id(addr: str):
        i = addr2id.get(addr)
        if i is None:
            i = len(addr2id) + 1
            addr2id[addr] = i
        return i

    # ---- NEW: pre-resolve comma-adjacent (child -> parent) pairs ----
    adjacent_pairs = toponym_text_indices.get('__adjacent__', set()) or set()
    def _ensure_tuple(c):
        if 'addr_tuple' not in c:
            c['addr_tuple'] = tuple(s.strip().lower() for s in c['address'].split(',') if s.strip())
        elif isinstance(c['addr_tuple'], list):
            c['addr_tuple'] = tuple(c['addr_tuple'])
        return c['addr_tuple']
    for child, parent in list(adjacent_pairs):
        if child in merged_toponyms and parent in merged_toponyms \
           and merged_toponyms[child] and merged_toponyms[parent]:
            best_pair = None
            best_score = -1.0
            for c in merged_toponyms[child]:
                _ensure_tuple(c)
            for p in merged_toponyms[parent]:
                _ensure_tuple(p)
            for c in merged_toponyms[child]:
                for p in merged_toponyms[parent]:
                    if not _is_child_of_with_gap(c['addr_tuple'], p['addr_tuple'], max_skip=1):
                        continue
                    sim_c = similarity_cache[(child, c['name'], tuple(c.get('alt_names', [])))]
                    sim_p = similarity_cache[(parent, p['name'], tuple(p.get('alt_names', [])))]
                    base_c = sim_c*weight_similarity + normalize_admin_level(c['admin_level'])*weight_level + compute_population_score(c['population'])*weight_population
                    base_p = sim_p*weight_similarity+ normalize_admin_level(p['admin_level'])*weight_level + compute_population_score(p['population'])*weight_population

                    pair_total = base_c + base_p + spatial_weight
                    if pair_total > best_score:
                        best_score = pair_total
                        best_pair = (c, p)
            if best_pair:
                merged_toponyms[child]  = [best_pair[0]]
                merged_toponyms[parent] = [best_pair[1]]

    # ---- function to (re)build top_feature_cache from current merged_toponyms ----
    # FIX: keep a SINGLE mapping of address->id that matches the cache and worker
    addrid_by_addr = {}  # <-- NEW shared mapping

    def _build_top_feature_cache():
        """
        Construct feature cache for all toponyms:
        - stores coordinates, address tuples, similarity arrays, and candidate metadata.
        Enables fast spatial and hierarchical computation.
        """

        top_feature_cache = {}
        for other_top, cand_list in merged_toponyms.items():
            if not cand_list:
                continue
            size = len(cand_list)
            lats = np.empty(size, dtype=np.float64)
            lons = np.empty(size, dtype=np.float64)
            addr_tuples = []
            sim_arr = np.empty(size, dtype=np.float64)
            addr_ids = []
            for k, c in enumerate(cand_list):
                lats[k] = c['lat']
                lons[k] = c['lon']
                if 'addr_tuple' not in c:
                    c['addr_tuple'] = tuple(s.strip().lower() for s in c['address'].split(',') if s.strip())
                elif isinstance(c['addr_tuple'], list):
                    c['addr_tuple'] = tuple(c['addr_tuple'])
                if 'addr_id' not in c:
                    c['addr_id'] = get_addr_id(c['address'])
                # FIX: record in the shared mapping
                addrid_by_addr[c['address']] = c['addr_id']  # <-- NEW

                addr_ids.append(c['addr_id'])
                addr_tuples.append(c['addr_tuple'])
                sim_key = (other_top.lower(), c['name'], tuple(c.get('alt_names', [])))
                sim_arr[k] = similarity_cache[sim_key]
            top_feature_cache[other_top.lower()] = {
                'lats': lats,
                'lons': lons,
                'addr_tuples': addr_tuples,
                'sim_arr': sim_arr,
                'cand_list': cand_list,
                'addr_ids': addr_ids
            }
        return top_feature_cache

    # ---- NEW: sequential scoring in text order + Top-10 pruning after each ----
    order = sorted(merged_toponyms.keys(), key=lambda k: min(toponym_text_indices.get(k, [0])) if toponym_text_indices.get(k) else 0)

    raw_rankings = {}
    for norm_top in order:
        if norm_top in not_process or not merged_toponyms.get(norm_top):
            continue

        top_feature_cache = _build_top_feature_cache()
        # FIX: pass the shared mapping down to the worker
        _init_worker(top_feature_cache, toponym_text_indices, similarity_cache, max_text_len, addrid_by_addr)  # <-- CHANGED CALL

        norm_top_scored, cand_scores = _score_one_toponym((norm_top, merged_toponyms[norm_top]), debug, spatial_weight, weight_similarity, weight_level, weight_population, distance_thres, sp_score_type, max_population)
        raw_rankings[norm_top_scored] = cand_scores

        if cand_scores:
            cand_scores.sort(key=lambda x: x[1], reverse=True)
            base_k = 5
            seen_addrs = set()
            top10 = []
            for c, s in cand_scores:
                top10.append(c)
                if c['address'] not in seen_addrs:
                    seen_addrs.add(c['address'])
                    if len(seen_addrs) >= base_k:
                        break
            merged_toponyms[norm_top] = top10
            
    # ---- Final merge to Top-N (unchanged) ----
    merged_results = {}
    merged_scores = {}
    for norm_top, candidate_scores in raw_rankings.items():
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        merged_candidates = {}
        for candidate, score in candidate_scores:
            addr = candidate['address']
            if addr not in merged_candidates or score > merged_candidates[addr]['score']:
                merged_candidates[addr] = {
                    'address': candidate['address'],
                    'lat': candidate['lat'],
                    'lon': candidate['lon'],
                    'score': score
                }
        sorted_items = sorted(merged_candidates.items(), key=lambda x: x[1]['score'], reverse=True)[:top_N]
        merged_results[norm_top] = [(item[1]['address'], item[1]['lat'], item[1]['lon'], item[1]['score'])
                                    for item in sorted_items]
        merged_scores[norm_top] = [item[1]['score'] for item in sorted_items]

    return merged_results, merged_scores
