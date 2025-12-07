"""
REAL Knowledge Graph with actual insights
"""
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import community as community_louvain  # pip install python-louvain

class KnowledgeGraphBuilder:
    """Build meaningful knowledge graph from customer feedback"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.insights = {}
    
    def build_from_comments(self, df):
        """Build graph showing REAL relationships"""
        print("🔗 Building Knowledge Graph...")
        
        # 1. Extract entities (simplified but real)
        entities = self._extract_entities(df)
        
        # 2. Build co-occurrence network
        self._build_cooccurrence_network(entities)
        
        # 3. Run network analysis
        self._analyze_network()
        
        # 4. Generate REAL insights
        self._generate_network_insights()
        
        return self.graph
    
    def _extract_entities(self, df):
        """Extract meaningful entities from comments"""
        entities_by_doc = []
        
        for idx, row in df.iterrows():
            entities = {
                'issues': [],
                'products': [],
                'sentiments': [],
                'customers': [f"customer_{row['contact_id']}"]
            }
            
            text = str(row['commentaire']).lower()
            
            # Extract REAL patterns
            if any(word in text for word in ['panne', 'bug', 'ne marche']):
                entities['issues'].append('technical_issue')
            if any(word in text for word in ['prix', 'cher', 'facture']):
                entities['issues'].append('billing_issue')
            if any(word in text for word in ['conseiller', 'service', 'attente']):
                entities['issues'].append('service_issue')
            
            # Products from offer_label
            if 'offer_label' in row:
                offer = str(row['offer_label'])
                if 'pop' in offer.lower():
                    entities['products'].append('FreeBox_Pop')
                elif 'ultra' in offer.lower():
                    entities['products'].append('FreeBox_Ultra')
            
            entities_by_doc.append(entities)
        
        return entities_by_doc
    
    def _build_cooccurrence_network(self, entities_by_doc):
        """Build network based on co-occurrence"""
        # Track co-occurrences
        cooccurrences = Counter()
        
        for entities in entities_by_doc:
            all_entities = []
            for category, items in entities.items():
                all_entities.extend(items)
            
            # Add edges for co-occurring entities
            for i in range(len(all_entities)):
                for j in range(i+1, len(all_entities)):
                    edge = tuple(sorted([all_entities[i], all_entities[j]]))
                    cooccurrences[edge] += 1
        
        # Build graph
        for (node1, node2), weight in cooccurrences.items():
            if weight >= 2:  # Only significant co-occurrences
                self.graph.add_edge(node1, node2, weight=weight)
        
        print(f"   Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def _analyze_network(self):
        """Run REAL network analysis"""
        if len(self.graph.nodes()) == 0:
            return
        
        # Centrality measures
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        
        # Community detection
        try:
            partition = community_louvain.best_partition(self.graph)
        except:
            partition = {node: 0 for node in self.graph.nodes()}
        
        self.insights = {
            'central_nodes': sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5],
            'bridging_nodes': sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5],
            'communities': len(set(partition.values())),
            'density': nx.density(self.graph)
        }
    
    def _generate_network_insights(self):
        """Generate ACTUAL business insights from graph"""
        insights_text = []
        
        if not self.insights.get('central_nodes'):
            return
        
        # Insight 1: Most connected issues
        central = self.insights['central_nodes']
        insights_text.append(f"**Most Central Issues**: {', '.join([n for n,_ in central[:3]])}")
        
        # Insight 2: Bridge analysis
        bridges = self.insights['bridging_nodes']
        if bridges:
            bridge_node, bridge_score = bridges[0]
            insights_text.append(f"**Key Bridge**: '{bridge_node}' connects different issue clusters (score: {bridge_score:.3f})")
        
        # Insight 3: Community structure
        if self.insights['communities'] > 1:
            insights_text.append(f"**Issue Clusters**: {self.insights['communities']} distinct problem clusters identified")
        
        # Save insights
        import json
        with open('results/knowledge_graph_insights.json', 'w') as f:
            json.dump({
                'insights': insights_text,
                'metrics': self.insights
            }, f, indent=2)
    
    def visualize(self):
        """Create interactive visualization"""
        if len(self.graph.nodes()) == 0:
            return None
        
        # Create Plotly figure
        pos = nx.spring_layout(self.graph, seed=42)
        
        edge_trace = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            ))
        
        node_trace = go.Scatter(
            x=[pos[node][0] for node in self.graph.nodes()],
            y=[pos[node][1] for node in self.graph.nodes()],
            mode='markers+text',
            text=list(self.graph.nodes()),
            textposition="top center",
            marker=dict(
                size=20,
                color=[len(list(self.graph.neighbors(node))) for node in self.graph.nodes()],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Connections')
            )
        )
        
        fig = go.Figure(data=edge_trace + [node_trace],
                       layout=go.Layout(
                           title='Customer Feedback Knowledge Graph',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40)
                       ))
        
        fig.write_html('results/knowledge_graph.html')
        return fig
