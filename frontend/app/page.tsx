'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';

type UserStory = { story: string; priority: 'MUST' | 'SHOULD' | 'COULD'; acceptance_criteria: string[] };
type Feature = { name: string; description: string; user_stories: UserStory[] };
type Capability = { name: string; description: string; features: Feature[] };
type Epic = { name: string; business_outcome: string; capabilities: Capability[] };
type ProductBrief = {
  product_name: string; tagline: string; vision: string; problem_statement: string;
  target_users: string[]; personas: { name: string; description: string; goals: string[]; frustrations: string[] }[];
  user_pain_points: string[]; desired_outcomes: string[]; business_value: string[]; success_metrics: string[];
  assumptions: string[]; uncertainties: string[]; mvp_scope: string[]; out_of_scope: string[];
  future_enhancements: string[]; epics: Epic[]; status: string;
};
type ProjectResponse = { id: string; name: string; status: string; agentRunId: string; discovery: { product_brief: ProductBrief; provider: string; model: string; warnings: string[] } };

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8080';

function List({ items }: { items: string[] }) {
  return <ul className="clean-list">{items.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>;
}

export default function Home() {
  const [idea, setIdea] = useState('');
  const [nameHint, setNameHint] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [project, setProject] = useState<ProjectResponse | null>(null);

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (idea.trim().length < 5) return;
    setBusy(true); setError(''); setProject(null);
    try {
      const response = await fetch(`${API}/api/projects`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: idea.trim(), productNameHint: nameHint.trim() || null })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail ?? payload.message ?? `API returned ${response.status}`);
      setProject(payload as ProjectResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not generate the product brief.');
    } finally { setBusy(false); }
  }

  const brief = project?.discovery.product_brief;
  return <main className="shell">
    <nav className="nav"><div className="brand"><span className="brand-mark">✳</span> product studio</div><span className="nav-label">PHASE 2 · PRODUCT MANAGER AGENT</span></nav>
    <section className="hero">
      <div className="eyebrow">FROM IDEA TO PRODUCT STRATEGY</div>
      <h1>Start with an idea.<br/><em>Get a product plan.</em></h1>
      <p className="subhead">Describe what you want to build. The Product Manager Agent turns it into a product brief, user personas, measurable outcomes and a prioritized delivery hierarchy.</p>
      <form className="composer" onSubmit={createProject}>
        <label htmlFor="idea">What do you want to build?</label>
        <textarea id="idea" value={idea} onChange={e => setIdea(e.target.value)} placeholder="For example: Build a social photo-sharing app where people can post photos, follow creators, and discover communities..." minLength={5} maxLength={8000} required />
        <label htmlFor="nameHint" className="secondary-label">Product name (optional)</label>
        <input id="nameHint" value={nameHint} onChange={e => setNameHint(e.target.value)} placeholder="Let the agent suggest a name" maxLength={180}/>
        <div className="composer-footer"><span>One sentence is enough. Missing details become documented assumptions.</span><button type="submit" disabled={busy || idea.trim().length < 5}>{busy ? 'Building product brief…' : 'Generate product brief →'}</button></div>
      </form>
      {error && <div className="error-panel" role="alert"><strong>Could not generate the brief</strong><p>{error}</p><small>Check that PostgreSQL, Spring Boot and the LangGraph agent service are running.</small></div>}
      {brief && <section className="brief" aria-live="polite">
        <div className="brief-top"><div><div className="eyebrow">PRODUCT BRIEF GENERATED</div><h2>{brief.product_name}</h2><p>{brief.tagline}</p></div><span className="status-pill">{project.status}</span></div>
        {project.discovery.warnings.map(w => <div className="warning" key={w}>{w}</div>)}
        <div className="meta-line"><span>Project ID <code>{project.id}</code></span><span>Provider <code>{project.discovery.provider} / {project.discovery.model}</code></span></div>
        <div className="brief-grid">
          <article className="brief-card wide"><h3>Product vision</h3><p>{brief.vision}</p><h3>Problem statement</h3><p>{brief.problem_statement}</p></article>
          <article className="brief-card"><h3>Target users</h3><List items={brief.target_users}/></article>
          <article className="brief-card"><h3>User pain points</h3><List items={brief.user_pain_points}/></article>
          <article className="brief-card"><h3>Desired outcomes</h3><List items={brief.desired_outcomes}/></article>
          <article className="brief-card"><h3>Business value</h3><List items={brief.business_value}/></article>
          <article className="brief-card"><h3>Success metrics</h3><List items={brief.success_metrics}/></article>
          <article className="brief-card"><h3>Assumptions</h3><List items={brief.assumptions}/></article>
          <article className="brief-card"><h3>Material uncertainties</h3><List items={brief.uncertainties}/></article>
          <article className="brief-card"><h3>MVP scope</h3><List items={brief.mvp_scope}/></article>
          <article className="brief-card"><h3>Out of scope</h3><List items={brief.out_of_scope}/></article>
        </div>
        <div className="brief-card hierarchy"><div className="hierarchy-head"><div><div className="eyebrow">PRODUCT BACKLOG</div><h3>Epic → Capability → Feature → User story</h3></div><span>{brief.epics.length} epics</span></div>
          {brief.epics.map((epic, ei) => <div className="epic" key={`${ei}-${epic.name}`}><div className="level-label">EPIC {ei + 1}</div><h4>{epic.name}</h4><p>{epic.business_outcome}</p>
            {epic.capabilities.map((cap, ci) => <div className="capability" key={`${ci}-${cap.name}`}><div className="level-label">CAPABILITY</div><h5>{cap.name}</h5><p>{cap.description}</p>
              {cap.features.map((feature, fi) => <div className="feature" key={`${fi}-${feature.name}`}><div className="level-label">FEATURE</div><strong>{feature.name}</strong><p>{feature.description}</p>
                {feature.user_stories.map((story, si) => <div className="story" key={`${si}-${story.story}`}><div className="story-title"><span>{story.story}</span><span className={`priority ${story.priority.toLowerCase()}`}>{story.priority}</span></div><div className="level-label">ACCEPTANCE CRITERIA</div><List items={story.acceptance_criteria}/></div>)}
              </div>)}
            </div>)}
          </div>)}
        </div>
        <div className="personas"><div className="eyebrow">USER PERSONAS</div><div className="persona-grid">{brief.personas.map((persona, i) => <article className="brief-card" key={`${i}-${persona.name}`}><h3>{persona.name}</h3><p>{persona.description}</p><strong>Goals</strong><List items={persona.goals}/><strong>Frustrations</strong><List items={persona.frustrations}/></article>)}</div></div>
        <div className="next-step"><div><strong>Product discovery complete</strong><p>Review and refine this brief before handing it to the Design Agent.</p></div><span className="status-pill">READY FOR REVIEW</span></div>
      </section>}
      <div className="pipeline"><div><b>01</b><strong>Discover</strong><small>Product brief & backlog</small></div><i>→</i><div><b>02</b><strong>Design</strong><small>UX & Figma handoff</small></div><i>→</i><div><b>03</b><strong>Build</strong><small>Code & integrations</small></div><i>→</i><div><b>04</b><strong>Deliver</strong><small>QA, docs & live URL</small></div></div>
    </section>
    <footer><span>AI PRODUCT STUDIO</span><span>PHASE 2 · PRODUCT MANAGER AGENT</span></footer>
  </main>;
}
