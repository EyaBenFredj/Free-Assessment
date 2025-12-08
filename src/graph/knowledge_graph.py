#!/usr/bin/env python3
"""
Knowledge Graph Builder - Fixed with correct database path
"""
from pathlib import Path
import sqlite3
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import time

# CORRECT DATABASE PATH - From your message
DB_PATH = Path(r"C:\Users\eyabe\PycharmProjects\Free_Project\data\db.sqlite")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "graph"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def explore_database():
    """Explore what's in the database."""
    print("=" * 70)
    print("EXPLORING DATABASE")
    print("=" * 70)

    print(f"Database path: {DB_PATH}")
    print(f"Database exists: {DB_PATH.exists()}")

    current_db_path = DB_PATH

    if not current_db_path.exists():
        print(f"ERROR: Database not found at {current_db_path}")
        # Try to find it
        possible_paths = [
            current_db_path,
            PROJECT_ROOT / "data" / "db.sqlite",
            Path("data/db.sqlite"),
            Path("../data/db.sqlite"),
        ]

        for path in possible_paths:
            if path.exists():
                print(f"Found database at: {path}")
                current_db_path = path
                break

        if not current_db_path.exists():
            raise FileNotFoundError(f"Database not found! Checked: {possible_paths}")

    conn = sqlite3.connect(str(current_db_path))
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\nTables found ({len(tables)}):")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")

        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count:,}")
        except:
            print(f"    (Could not count rows)")

        # Get column info
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"    Columns ({len(columns)}): {col_names[:10]}")
            if len(columns) > 10:
                print(f"    ... and {len(columns) - 10} more")

            # Check for text columns
            text_keywords = ['comment', 'text', 'verbatim', 'feedback', 'avis', 'message']
            text_cols = [col for col in col_names
                         if any(keyword in col.lower() for keyword in text_keywords)]
            if text_cols:
                print(f"    Possible text columns: {text_cols}")

        except:
            print(f"    (Could not get column info)")

    return tables, conn, current_db_path


def find_comments_table(conn, tables):
    """Find the table that contains comments/text."""
    print("\n" + "=" * 70)
    print("SEARCHING FOR COMMENTS/TEXT DATA")
    print("=" * 70)

    candidate_tables = []

    for table_name, in tables:
        try:
            # Get column names
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # Check for text-like columns
            text_columns = []
            for col in columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in
                       ['comment', 'text', 'verbatim', 'feedback', 'avis',
                        'message', 'description', 'note', 'content', 'review']):
                    text_columns.append(col)

            if text_columns:
                # Check sample data from first text column
                sample_col = text_columns[0]
                cursor.execute(f"SELECT {sample_col} FROM {table_name} LIMIT 5")
                samples = cursor.fetchall()

                # See if it looks like text
                text_samples = []
                for sample in samples:
                    if sample and sample[0]:
                        text = str(sample[0])
                        if len(text) > 20:
                            text_samples.append(text)

                if text_samples:
                    candidate_tables.append((table_name, sample_col, len(text_samples)))

                    print(f"\nFound candidate table: {table_name}")
                    print(f"  Text column: {sample_col}")
                    print(f"  Sample data:")
                    for i, text in enumerate(text_samples[:3]):
                        print(f"    {i + 1}. {text[:100]}...")

        except Exception as e:
            continue

    if not candidate_tables:
        print("No obvious comments table found. Checking all tables...")

        for table_name, in tables[:5]:  # Check first 5 tables
            try:
                # Get a few rows to see content
                df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 10", conn)
                print(f"\n=== Table: {table_name} ===")
                print(f"Shape: {df.shape}")
                print("Columns:", list(df.columns))

                # Look for any text columns
                for col in df.columns:
                    if df[col].dtype == 'object':
                        # Check if column contains text
                        non_empty = df[col].dropna()
                        if len(non_empty) > 0:
                            sample = str(non_empty.iloc[0])
                            if len(sample) > 30 and ' ' in sample:
                                print(f"\nPossible text column '{col}':")
                                print(f"  Sample: {sample[:100]}...")
                                candidate_tables.append((table_name, col, len(df)))

                # If df is small, show all data
                if len(df) <= 5:
                    print("\nData:")
                    print(df.to_string())

            except Exception as e:
                print(f"  Error reading {table_name}: {e}")

    return candidate_tables


def load_comments_data(conn, table_name, text_column, sample_size=None):
    """Load comments from the specified table."""
    print(f"\n" + "=" * 70)
    print(f"LOADING DATA FROM: {table_name}.{text_column}")
    print("=" * 70)

    # Get total count
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    print(f"Total rows in table: {total_rows:,}")

    # Build query
    if sample_size and sample_size < total_rows:
        query = f"""
        SELECT {text_column} 
        FROM {table_name} 
        WHERE {text_column} IS NOT NULL 
        AND TRIM({text_column}) != ''
        ORDER BY RANDOM()
        LIMIT {sample_size}
        """
        print(f"Loading random sample of {sample_size} rows...")
    else:
        query = f"""
        SELECT {text_column} 
        FROM {table_name} 
        WHERE {text_column} IS NOT NULL 
        AND TRIM({text_column}) != ''
        """
        print(f"Loading ALL {total_rows:,} rows...")

    # Execute query
    df = pd.read_sql(query, conn)
    print(f"Loaded {len(df):,} non-empty comments")

    if len(df) == 0:
        print("WARNING: No comments found!")
        return [], text_column

    # Get the actual column name (case might differ)
    actual_text_column = df.columns[0]

    # Clean the text
    df[actual_text_column] = df[actual_text_column].astype(str).str.strip()

    # Remove any remaining empty strings
    df = df[df[actual_text_column] != ""]
    print(f"After cleaning: {len(df):,} comments")

    # Show statistics
    print(f"\n=== TEXT STATISTICS ===")
    print(f"Average length: {df[actual_text_column].str.len().mean():.1f} characters")
    print(f"Min length: {df[actual_text_column].str.len().min():.1f} characters")
    print(f"Max length: {df[actual_text_column].str.len().max():.1f} characters")

    # Show samples
    print(f"\n=== SAMPLE COMMENTS (first 5) ===")
    for i in range(min(5, len(df))):
        text = df[actual_text_column].iloc[i]
        print(f"{i + 1}. {text[:150]}..." if len(text) > 150 else f"{i + 1}. {text}")

    return df[actual_text_column].tolist(), actual_text_column


def extract_entities_simple(texts):
    """Simple but effective entity extraction."""
    print(f"\n" + "=" * 70)
    print(f"EXTRACTING ENTITIES FROM {len(texts):,} COMMENTS")
    print("=" * 70)

    # Common French business terms
    business_terms = [
        'service', 'client', 'technique', 'support', 'fibre', 'internet',
        'conseiller', 'prix', 'qualité', 'installation', 'débit', 'vitesse',
        'panne', 'problème', 'réseau', 'appel', 'téléphone', 'équipe',
        'solution', 'satisfait', 'mécontent', 'déçu', 'content', 'heureux',
        'rapide', 'lent', 'excellent', 'mauvais', 'bon', 'correct',
        'agent', 'technicien', 'commercial', 'contrat', 'facture', 'forfait',
        'mobile', 'fixe', 'box', 'wifi', 'dépannage', 'intervention', 'rdv',
        'attente', 'temps', 'réponse', 'information', 'conseil', 'aide',
        'assistance', 'accompagnement', 'sav'
    ]

    all_entities = []
    entity_counter = Counter()

    print("Processing comments...")
    start_time = time.time()

    for i, text in enumerate(texts):
        text_lower = text.lower()

        # Find business terms
        found_terms = []
        for term in business_terms:
            if term in text_lower:
                found_terms.append(term.capitalize())

        # Extract capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-ZÉÈÀÂÊÎÔÛËÏÜÇ][a-zéèàâêîôûëïüç]+\b', text)

        # Extract product names (like Freebox, Livebox, etc.)
        products = re.findall(r'\b(?:Freebox|Livebox|Bouygues|SFR|Orange|Box)\w*\b', text, re.IGNORECASE)

        # Combine all entities
        entities = list(set(found_terms + capitalized + [p.capitalize() for p in products]))

        # Remove very short entities
        entities = [e for e in entities if len(e) > 2]

        # Update counters
        for entity in entities:
            entity_counter[entity] += 1

        all_entities.append(entities)

        # Progress indicator
        if (i + 1) % 5000 == 0 and i > 0:
            elapsed = time.time() - start_time
            print(f"  Processed {i + 1:,} comments ({elapsed:.1f}s)...")

    elapsed = time.time() - start_time

    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Time: {elapsed:.1f} seconds")
    print(f"Total entity occurrences: {sum(entity_counter.values()):,}")
    print(f"Unique entities: {len(entity_counter):,}")

    # Show top entities
    if entity_counter:
        print(f"\n=== TOP 30 ENTITIES ===")
        for entity, count in entity_counter.most_common(30):
            percentage = (count / len(texts)) * 100 if texts else 0
            print(f"  {entity}: {count:,} ({percentage:.1f}%)")

    return all_entities, entity_counter


def build_knowledge_graph(entities_list, entity_counts, min_count=2):
    """Build co-occurrence graph."""
    print(f"\n" + "=" * 70)
    print(f"BUILDING KNOWLEDGE GRAPH (min_count={min_count})")
    print("=" * 70)

    # Filter entities by minimum frequency
    print(f"Filtering entities...")
    filtered_entities = {e: c for e, c in entity_counts.items() if c >= min_count}

    print(f"  Before filtering: {len(entity_counts):,} entities")
    print(f"  After filtering: {len(filtered_entities):,} entities")

    if not filtered_entities:
        print(f"WARNING: No entities with frequency ≥ {min_count}!")
        print(f"Highest frequency: {max(entity_counts.values()) if entity_counts else 0}")
        print(f"Trying with min_count=1...")
        filtered_entities = entity_counts

    if not filtered_entities:
        print(f"ERROR: Still no entities!")
        return nx.Graph(), entity_counts

    # Build co-occurrence matrix
    print("Building co-occurrence matrix...")
    cooccurrence = Counter()

    for doc_entities in entities_list:
        # Get filtered entities in this document
        filtered_doc_entities = [e for e in set(doc_entities) if e in filtered_entities]

        # Count co-occurrences
        for i in range(len(filtered_doc_entities)):
            for j in range(i + 1, len(filtered_doc_entities)):
                # Sort to ensure consistent ordering
                a, b = sorted([filtered_doc_entities[i], filtered_doc_entities[j]])
                cooccurrence[(a, b)] += 1

    # Build graph
    print("Creating graph...")
    G = nx.Graph()

    # Add nodes with frequency attribute
    for entity, freq in filtered_entities.items():
        G.add_node(entity, frequency=freq)

    # Add edges with weight
    for (a, b), weight in cooccurrence.items():
        G.add_edge(a, b, weight=weight)

    print(f"\n=== GRAPH CREATED ===")
    print(f"Nodes: {G.number_of_nodes():,}")
    print(f"Edges: {G.number_of_edges():,}")

    if G.number_of_nodes() > 0:
        # Calculate graph metrics
        degrees = [deg for _, deg in G.degree()]
        print(f"Average degree: {sum(degrees) / len(degrees):.1f}")
        print(f"Max degree: {max(degrees)}")

        # Connected components
        components = list(nx.connected_components(G))
        print(f"Connected components: {len(components)}")

        if components:
            largest = max(components, key=len)
            print(f"Largest component: {len(largest):,} nodes ({len(largest) / G.number_of_nodes() * 100:.1f}%)")

        # Show hub nodes
        print(f"\n=== TOP 10 HUB NODES ===")
        hub_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
        for node, degree in hub_nodes:
            freq = entity_counts.get(node, 0)
            print(f"  {node}: {degree} connections (appears {freq:,} times)")

    return G, entity_counts


def create_visualizations(G, counts):
    """Create visualizations of the graph."""
    print(f"\n" + "=" * 70)
    print(f"CREATING VISUALIZATIONS")
    print("=" * 70)

    if G.number_of_nodes() == 0:
        print("No nodes to visualize!")
        return None, None

    # 1. PNG visualization
    print("Creating static visualization (PNG)...")
    try:
        plt.figure(figsize=(14, 10))

        # Use spring layout
        pos = nx.spring_layout(G, seed=42, k=1.5, iterations=50)

        # Node sizes based on frequency
        node_sizes = []
        for node in G.nodes():
            freq = counts.get(node, 1)
            size = 300 + min(1000, freq * 10)
            node_sizes.append(size)

        # Edge widths based on weight
        edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

        # Draw
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                               node_color='lightblue', alpha=0.8,
                               edgecolors='darkblue', linewidths=2)

        if edge_weights:
            if max(edge_weights) > 0:
                edge_widths = [max(1, w * 2) for w in edge_weights]
                nx.draw_networkx_edges(G, pos, width=edge_widths,
                                       alpha=0.6, edge_color='gray')

        # Labels
        if G.number_of_nodes() <= 50:
            nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        else:
            # Only label important nodes
            degrees = dict(G.degree())
            labels = {node: node for node in G.nodes() if degrees.get(node, 0) > 2}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=9)

        plt.title(f"Knowledge Graph - {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges",
                  fontsize=14, pad=20)
        plt.axis('off')

        png_path = RESULTS_DIR / "knowledge_graph.png"
        plt.savefig(png_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ PNG saved: {png_path}")

    except Exception as e:
        print(f"Error creating PNG: {e}")
        png_path = None

    # 2. HTML interactive visualization
    print("\nCreating interactive visualization (HTML)...")
    html_path = None

    try:
        from pyvis.network import Network

        # Use all nodes for small graphs, subset for large ones
        if G.number_of_nodes() > 100:
            print(f"  Note: Graph has {G.number_of_nodes():,} nodes, showing top 100")
            # Get top nodes by degree
            degrees = dict(G.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:100]
            top_node_names = [node for node, _ in top_nodes]
            H = G.subgraph(top_node_names).copy()
        else:
            H = G

        net = Network(height="700px", width="100%", notebook=False,
                      bgcolor="#ffffff", font_color="black")

        # Add nodes
        for node in H.nodes():
            freq = counts.get(node, 0)
            degree = H.degree(node)
            size = 20 + min(50, degree * 3)

            title = f"{node}\nFrequency: {freq}\nConnections: {degree}"
            net.add_node(node, label=node, title=title, size=size)

        # Add edges
        for u, v, data in H.edges(data=True):
            weight = data.get('weight', 1)
            width = max(1, min(5, weight))
            net.add_edge(u, v, value=weight, width=width)

        # Configure physics
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          }
        }
        """)

        html_path = RESULTS_DIR / "knowledge_graph.html"
        net.save_graph(str(html_path))
        print(f"✓ HTML saved: {html_path}")

    except ImportError:
        print("  Note: Install pyvis for interactive graph: pip install pyvis")
    except Exception as e:
        print(f"  Error creating HTML: {e}")

    return png_path, html_path


def save_data(G, counts, texts, entities_list, db_path):
    """Save all data to files."""
    print(f"\n" + "=" * 70)
    print(f"SAVING DATA")
    print("=" * 70)

    # 1. Save entity frequencies
    if counts:
        freq_df = pd.DataFrame.from_dict(counts, orient='index', columns=['frequency'])
        freq_df = freq_df.sort_values('frequency', ascending=False)

        freq_path = RESULTS_DIR / "entity_frequencies.csv"
        freq_df.to_csv(freq_path, encoding='utf-8')
        print(f"✓ Entity frequencies: {freq_path}")

    # 2. Save graph edges
    if G.number_of_nodes() > 0:
        edges_data = []
        for u, v, data in G.edges(data=True):
            edges_data.append({
                'source': u,
                'target': v,
                'weight': data.get('weight', 1)
            })

        edges_df = pd.DataFrame(edges_data)
        edges_path = RESULTS_DIR / "graph_edges.csv"
        edges_df.to_csv(edges_path, index=False, encoding='utf-8')
        print(f"✓ Graph edges: {edges_path}")

        # Save nodes
        nodes_data = []
        for node in G.nodes():
            nodes_data.append({
                'node': node,
                'frequency': counts.get(node, 0),
                'degree': G.degree(node)
            })

        nodes_df = pd.DataFrame(nodes_data)
        nodes_path = RESULTS_DIR / "graph_nodes.csv"
        nodes_df.to_csv(nodes_path, index=False, encoding='utf-8')
        print(f"✓ Graph nodes: {nodes_path}")

    # 3. Save summary
    report_path = RESULTS_DIR / "summary.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("KNOWLEDGE GRAPH SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Database: {db_path}\n\n")
        f.write(f"Comments processed: {len(texts)}\n")
        f.write(f"Graph nodes: {G.number_of_nodes()}\n")
        f.write(f"Graph edges: {G.number_of_edges()}\n\n")

        if counts:
            f.write("Top 20 entities:\n")
            for entity, count in Counter(counts).most_common(20):
                f.write(f"  {entity}: {count}\n")

    print(f"✓ Summary: {report_path}")


def main():
    """Main function."""
    print("=" * 60)
    print("KNOWLEDGE GRAPH BUILDER")
    print("=" * 60)

    start_time = time.time()

    try:
        # 1. Explore database
        tables, conn, used_db_path = explore_database()

        # 2. Find comments table
        candidate_tables = find_comments_table(conn, tables)

        if not candidate_tables:
            print("\nERROR: No suitable table found!")
            conn.close()
            return

        # Use first candidate
        table_name, text_column, _ = candidate_tables[0]
        print(f"\nUsing table: {table_name}.{text_column}")

        # 3. Ask for sample size
        use_full = input("\nProcess full dataset? (y/n, default=y): ").strip().lower()
        sample_size = None

        if use_full == 'n':
            try:
                sample_size = int(input("Sample size (e.g., 1000): ").strip())
            except:
                sample_size = 1000
            print(f"Using sample of {sample_size} rows")
        else:
            print("Processing ALL data")

        # 4. Load data
        texts, text_column = load_comments_data(conn, table_name, text_column, sample_size)
        conn.close()

        if not texts:
            print("ERROR: No text data loaded!")
            return

        # 5. Extract entities
        entities_list, entity_counts = extract_entities_simple(texts)

        if not entity_counts:
            print("WARNING: No entities extracted!")
            print("Creating empty graph...")
            G = nx.Graph()
        else:
            # 6. Determine min_count
            highest_freq = max(entity_counts.values())
            suggested_min = max(1, highest_freq // 20)  # 5% of max

            print(f"\nEntity frequency range: 1 to {highest_freq}")
            print(f"Suggested min_count: {suggested_min} (5% of max)")

            try:
                min_count_input = input(f"Enter min_count (default={suggested_min}): ").strip()
                min_count = int(min_count_input) if min_count_input else suggested_min
            except:
                min_count = suggested_min

            # 7. Build graph
            G, counts = build_knowledge_graph(entities_list, entity_counts, min_count)

        # 8. Create visualizations
        png_path, html_path = create_visualizations(G, entity_counts)

        # 9. Save data
        save_data(G, entity_counts, texts, entities_list, used_db_path)

        # 10. Summary
        elapsed = time.time() - start_time
        print(f"\n" + "=" * 60)
        print("PROCESS COMPLETE!")
        print("=" * 60)
        print(f"Total time: {elapsed:.1f} seconds")
        print(f"Comments processed: {len(texts):,}")
        print(f"Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

        if png_path:
            print(f"Static graph: {png_path}")
        if html_path:
            print(f"Interactive graph: {html_path}")
            print(f"\nOpen in browser: file://{html_path.absolute()}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()