"""
Network Clustering Service for Event Networking AI System
Community detection and network analysis for event attendee visualization
"""

import networkx as nx
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from models.database import User, Event, EventAttendee
from models.schemas import ClusterAnalysisResponse, Cluster, ClusterMember, NetworkData, NetworkNode, NetworkEdge
from services.recommendation_engine import RecommendationEngine
from utils.helpers import generate_color_palette

logger = logging.getLogger(__name__)


class ClusteringService:
    """Network clustering service for community detection"""

    def __init__(self):
        self.recommendation_engine = RecommendationEngine()

    def create_network_graph(self, db: Session, event_id: int) -> nx.Graph:
        """Create a NetworkX graph from event attendees"""
        try:
            # Get attendee data
            df = self.recommendation_engine.get_event_attendees_data(db, event_id)

            if df.empty or len(df) < 2:
                return nx.Graph()

            # Create graph
            G = nx.Graph()

            # Add nodes
            for _, user in df.iterrows():
                G.add_node(
                    user['user_id'],
                    name=user['name'],
                    company=user['company'],
                    industry=user['industry'],
                    job_title=user['job_title']
                )

            # Create features and similarity matrix
            features = self.recommendation_engine.create_user_features(df)
            if features.size > 0:
                similarity_matrix = self.recommendation_engine.calculate_similarity_matrix(features)

                # Add edges based on similarity threshold
                similarity_threshold = 0.3
                for i in range(len(df)):
                    for j in range(i + 1, len(df)):
                        if similarity_matrix[i, j] > similarity_threshold:
                            user1_id = df.iloc[i]['user_id']
                            user2_id = df.iloc[j]['user_id']
                            G.add_edge(user1_id, user2_id, weight=similarity_matrix[i, j])

            return G

        except Exception as e:
            logger.error(f"Error creating network graph: {str(e)}")
            return nx.Graph()

    def detect_communities(self, G: nx.Graph, algorithm: str = "louvain") -> Dict[int, int]:
        """Detect communities using specified algorithm"""
        try:
            if len(G.nodes()) < 3:
                return {node: 0 for node in G.nodes()}

            if algorithm == "louvain":
                communities = nx.algorithms.community.greedy_modularity_communities(G)
            elif algorithm == "girvan_newman":
                communities = list(nx.algorithms.community.girvan_newman(G))
                communities = communities[0] if communities else [set(G.nodes())]
            elif algorithm == "label_propagation":
                communities = nx.algorithms.community.label_propagation_communities(G)
            else:
                communities = nx.algorithms.community.greedy_modularity_communities(G)

            # Create mapping
            community_mapping = {}
            for community_id, community in enumerate(communities):
                for user_id in community:
                    community_mapping[user_id] = community_id

            return community_mapping

        except Exception as e:
            logger.error(f"Error in community detection: {str(e)}")
            return {node: 0 for node in G.nodes()}

    def analyze_clusters(self, db: Session, event_id: int,
                         algorithm: str = "louvain",
                         min_cluster_size: int = 2) -> ClusterAnalysisResponse:
        """Perform comprehensive cluster analysis"""
        try:
            # Get event
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                raise ValueError(f"Event {event_id} not found")

            # Create network graph
            G = self.create_network_graph(db, event_id)

            if len(G.nodes()) == 0:
                return ClusterAnalysisResponse(
                    event_id=event_id,
                    event_name=event.name,
                    algorithm_used=algorithm,
                    clusters=[],
                    cluster_stats={
                        "total_nodes": 0,
                        "total_edges": 0,
                        "num_clusters": 0,
                        "modularity": 0.0
                    },
                    analysis_timestamp=datetime.now()
                )

            # Detect communities
            community_mapping = self.detect_communities(G, algorithm)

            # Create clusters
            clusters = self._create_clusters(db, G, community_mapping, min_cluster_size)

            # Calculate statistics
            cluster_stats = self._calculate_cluster_stats(G, community_mapping)

            return ClusterAnalysisResponse(
                event_id=event_id,
                event_name=event.name,
                algorithm_used=algorithm,
                clusters=clusters,
                cluster_stats=cluster_stats,
                analysis_timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error in cluster analysis: {str(e)}")
            raise

    def _create_clusters(self, db: Session, G: nx.Graph,
                         community_mapping: Dict[int, int],
                         min_cluster_size: int) -> List[Cluster]:
        """Create cluster objects from community mapping"""
        clusters_dict = {}

        for user_id, cluster_id in community_mapping.items():
            if cluster_id not in clusters_dict:
                clusters_dict[cluster_id] = {
                    "members": [],
                    "industries": []
                }

            # Get user info
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                member = ClusterMember(
                    user_id=user_id,
                    name=user.name,
                    company=user.company,
                    job_title=user.job_title,
                    industry=user.industry,
                    degree=G.degree(user_id) if user_id in G.nodes else 0
                )

                clusters_dict[cluster_id]["members"].append(member)
                if user.industry:
                    clusters_dict[cluster_id]["industries"].append(user.industry)

        # Create final clusters
        clusters = []
        for cluster_id, data in clusters_dict.items():
            if len(data["members"]) >= min_cluster_size:
                # Find dominant industry
                industry_counts = pd.Series(data["industries"]).value_counts()
                dominant_industry = industry_counts.index[0] if len(industry_counts) > 0 else None

                cluster = Cluster(
                    cluster_id=cluster_id,
                    size=len(data["members"]),
                    members=data["members"],
                    dominant_industry=dominant_industry,
                    cluster_strength=0.75,  # Simplified calculation
                    common_interests=[]
                )
                clusters.append(cluster)

        return clusters

    def _calculate_cluster_stats(self, G: nx.Graph, community_mapping: Dict[int, int]) -> Dict:
        """Calculate comprehensive cluster statistics"""
        try:
            num_nodes = len(G.nodes())
            num_edges = len(G.edges())
            num_clusters = len(set(community_mapping.values()))

            # Calculate modularity
            communities = []
            cluster_dict = {}
            for user_id, cluster_id in community_mapping.items():
                if cluster_id not in cluster_dict:
                    cluster_dict[cluster_id] = set()
                cluster_dict[cluster_id].add(user_id)

            communities = list(cluster_dict.values())
            modularity = 0.0
            if len(communities) > 1:
                try:
                    modularity = nx.algorithms.community.modularity(G, communities)
                except:
                    modularity = 0.0

            cluster_sizes = [len(cluster) for cluster in communities]

            return {
                "total_nodes": num_nodes,
                "total_edges": num_edges,
                "num_clusters": num_clusters,
                "modularity": round(modularity, 3),
                "avg_cluster_size": round(np.mean(cluster_sizes), 2) if cluster_sizes else 0,
                "largest_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
                "smallest_cluster_size": min(cluster_sizes) if cluster_sizes else 0
            }

        except Exception as e:
            logger.error(f"Error calculating cluster stats: {str(e)}")
            return {}

    def export_network_for_visualization(self, db: Session, event_id: int) -> NetworkData:
        """Export network data for visualization tools"""
        try:
            # Create network graph
            G = self.create_network_graph(db, event_id)

            if len(G.nodes()) == 0:
                return NetworkData(
                    event_id=event_id,
                    nodes=[],
                    edges=[],
                    metadata={},
                    generated_at=datetime.now()
                )

            # Detect communities for coloring
            community_mapping = self.detect_communities(G)
            colors = generate_color_palette(len(set(community_mapping.values())))

            # Create nodes
            nodes = []
            for node_id in G.nodes():
                user = db.query(User).filter(User.id == node_id).first()
                if user:
                    cluster_id = community_mapping.get(node_id, 0)

                    node = NetworkNode(
                        id=node_id,
                        name=user.name,
                        company=user.company,
                        industry=user.industry,
                        job_title=user.job_title,
                        cluster=cluster_id,
                        degree=G.degree(node_id),
                        size=max(10, G.degree(node_id) * 3),
                        color=colors[cluster_id % len(colors)]
                    )
                    nodes.append(node)

            # Create edges
            edges = []
            for edge in G.edges(data=True):
                edge_obj = NetworkEdge(
                    source=edge[0],
                    target=edge[1],
                    weight=edge[2].get('weight', 1.0),
                    similarity_type="cosine_similarity"
                )
                edges.append(edge_obj)

            # Metadata
            metadata = {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "num_clusters": len(set(community_mapping.values())),
                "algorithm_used": "greedy_modularity"
            }

            return NetworkData(
                event_id=event_id,
                nodes=nodes,
                edges=edges,
                metadata=metadata,
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error exporting network data: {str(e)}")
            return NetworkData(
                event_id=event_id,
                nodes=[],
                edges=[],
                metadata={"error": str(e)},
                generated_at=datetime.now()
            )
