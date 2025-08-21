#!/usr/bin/env python3
"""
Enhanced Visualization Suite
Combines Plotly (interactive networks) + Seaborn (statistical analysis)
"""

import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
OUTPUT_DIR = "enhanced_visualizations"

# Set styles
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

def create_analytics_dashboard(event_id=1):
    """Create a comprehensive analytics dashboard with multiple chart types"""
    print("📊 Creating Enhanced Analytics Dashboard...")
    print("✅ Creating multi-chart dashboard with sample data...")
    
    # Create realistic sample data for demonstration
    np.random.seed(42)
    industries = ['Technology', 'Healthcare', 'Finance', 'Marketing', 'Education']
    experience_levels = ['Junior', 'Mid', 'Senior', 'Executive']
    
    # Sample attendee data
    attendees_data = {
        'industry': np.random.choice(industries, 50),
        'experience': np.random.choice(experience_levels, 50),
        'connections_made': np.random.poisson(5, 50),
        'similarity_score': np.random.beta(2, 5, 50),
        'satisfaction': np.random.normal(4.2, 0.8, 50)
    }
    
    df = pd.DataFrame(attendees_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Industry Distribution', 
            'Experience vs Connections',
            'Similarity Score Distribution',
            'Satisfaction by Industry'
        ),
        specs=[[{"type": "pie"}, {"type": "scatter"}],
               [{"type": "histogram"}, {"type": "box"}]]
    )
    
    # 1. Industry pie chart
    industry_counts = df['industry'].value_counts()
    fig.add_trace(
        go.Pie(labels=industry_counts.index, values=industry_counts.values),
        row=1, col=1
    )
    
    # 2. Experience vs connections scatter
    for exp in df['experience'].unique():
        subset = df[df['experience'] == exp]
        fig.add_trace(
            go.Scatter(
                x=subset.index, 
                y=subset['connections_made'],
                mode='markers',
                name=exp,
                showlegend=True
            ),
            row=1, col=2
        )
    
    # 3. Similarity score histogram
    fig.add_trace(
        go.Histogram(x=df['similarity_score'], name='Similarity'),
        row=2, col=1
    )
    
    # 4. Satisfaction box plot by industry
    for industry in df['industry'].unique():
        fig.add_trace(
            go.Box(
                y=df[df['industry'] == industry]['satisfaction'],
                name=industry,
                showlegend=False
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="🎯 Event Networking Analytics Dashboard",
            height=800,
            showlegend=True
        )
        
        # Save dashboard
        import os
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        fig.write_html(f"{OUTPUT_DIR}/analytics_dashboard.html")
        print(f"✅ Analytics dashboard saved to: {OUTPUT_DIR}/analytics_dashboard.html")
        
    # Create Seaborn statistical plots
    create_seaborn_analytics(df)

def create_seaborn_analytics(df):
    """Create beautiful statistical plots with Seaborn"""
    print("🎨 Creating Seaborn statistical visualizations...")
    
    # Set up the figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('📊 Statistical Analysis of Event Networking', fontsize=16, fontweight='bold')
    
    # 1. Industry distribution
    sns.countplot(data=df, x='industry', ax=axes[0,0], palette='viridis')
    axes[0,0].set_title('🏢 Attendee Industry Distribution')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # 2. Correlation heatmap
    numeric_cols = ['connections_made', 'similarity_score', 'satisfaction']
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=axes[0,1])
    axes[0,1].set_title('🔥 Correlation Heatmap')
    
    # 3. Experience vs connections violin plot
    sns.violinplot(data=df, x='experience', y='connections_made', ax=axes[1,0], palette='Set2')
    axes[1,0].set_title('🎻 Connections by Experience Level')
    
    # 4. Satisfaction distribution
    sns.histplot(data=df, x='satisfaction', kde=True, ax=axes[1,1], color='skyblue')
    axes[1,1].set_title('😊 Satisfaction Distribution')
    
    plt.tight_layout()
    
    # Save statistical plots
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(f"{OUTPUT_DIR}/statistical_analysis.png", dpi=300, bbox_inches='tight')
    print(f"✅ Statistical analysis saved to: {OUTPUT_DIR}/statistical_analysis.png")
    
    # Create additional specialized plots
    create_advanced_seaborn_plots(df)

def create_advanced_seaborn_plots(df):
    """Create more advanced seaborn visualizations"""
    print("🚀 Creating advanced statistical plots...")
    
    # Pairplot for relationships
    plt.figure(figsize=(12, 8))
    sns.pairplot(df[['connections_made', 'similarity_score', 'satisfaction', 'industry']], 
                 hue='industry', diag_kind='kde', palette='husl')
    plt.suptitle('🔍 Pairwise Relationships Analysis', y=1.02)
    plt.savefig(f"{OUTPUT_DIR}/pairwise_analysis.png", dpi=300, bbox_inches='tight')
    print(f"✅ Pairwise analysis saved to: {OUTPUT_DIR}/pairwise_analysis.png")
    plt.close()
    
    # Joint plot for detailed relationship
    plt.figure(figsize=(10, 8))
    sns.jointplot(data=df, x='similarity_score', y='connections_made', 
                  kind='reg', height=8, color='coral')
    plt.suptitle('📈 Similarity vs Connections Relationship', y=1.02)
    plt.savefig(f"{OUTPUT_DIR}/similarity_connections_joint.png", dpi=300, bbox_inches='tight')
    print(f"✅ Joint plot saved to: {OUTPUT_DIR}/similarity_connections_joint.png")
    plt.close()

def create_network_enhancement():
    """Enhanced network visualization with better styling"""
    print("🌐 Creating enhanced network visualization...")
    
    try:
        # Get cluster map data
        response = requests.get(f"{API_BASE_URL}/visualization/cluster-map?event_id=1")
        
        if response.status_code == 200:
            fig_data = response.json()
            
            # Create enhanced Plotly network
            fig = go.Figure(data=fig_data.get('data', []))
            
            # Enhanced styling
            fig.update_layout(
                title={
                    'text': "🕸️ Interactive Event Networking Map",
                    'x': 0.5,
                    'font': {'size': 20}
                },
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="💡 Hover over nodes to see attendee details. Zoom and pan to explore clusters.",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    font=dict(color="gray", size=10)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(248,248,248,1)',
                paper_bgcolor='white'
            )
            
            # Save enhanced network
            import os
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            fig.write_html(f"{OUTPUT_DIR}/enhanced_network_map.html")
            print(f"✅ Enhanced network map saved to: {OUTPUT_DIR}/enhanced_network_map.html")
            
        else:
            print(f"❌ Could not fetch network data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error creating enhanced network: {e}")

def main():
    """Run the enhanced visualization suite"""
    print("🎨 Enhanced Event Networking Visualization Suite")
    print("=" * 60)
    
    # Check server
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running!")
        else:
            print("❌ API Server not accessible")
            return
    except:
        print("❌ API Server not running. Please start it with: python main.py")
        return
    
    # Create all visualizations
    create_analytics_dashboard()
    create_network_enhancement()
    
    print("\n🎉 Enhanced Visualization Suite Complete!")
    print(f"📁 Check the '{OUTPUT_DIR}' folder for:")
    print("   📊 analytics_dashboard.html - Interactive business dashboard")
    print("   🌐 enhanced_network_map.html - Styled network visualization")
    print("   📈 statistical_analysis.png - Statistical analysis plots")
    print("   🔍 pairwise_analysis.png - Relationship analysis")
    print("   📊 similarity_connections_joint.png - Detailed correlation plot")

if __name__ == "__main__":
    main()