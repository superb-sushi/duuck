import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { post, get } from "./api";
import BountyListPage from "./pages/BountyListPage";
import NewBountySubmissionPage from "./pages/NewBountySubmissionPage";
import VideoSubmissionPage from "./pages/VideoSubmissionPage";
import VotingPage from "./pages/VotingPage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
    const [viewer, setViewer] = useState(null);
    const [creatorIds, setCreatorIds] = useState([]);
    const [videoIds, setVideoIds] = useState([]);
    const [sessionId, setSessionId] = useState(null);
    const [alloc, setAlloc] = useState(null);
    const [windowId, setWindowId] = useState("20250827T16");
    const [commitments, setCommitments] = useState([]);

    async function seed() {
        const v = await post("/viewer/create", { name: "Alice", weekly_budget: 7 });
        setViewer(v.id);
        const c1 = await post("/creator/create", { handle: "@chef" });
        const c2 = await post("/creator/create", { handle: "@dancer" });
        setCreatorIds([c1.id, c2.id]);
        const vid1 = await post("/video/create", { creator_id: c1.id, title: "Pasta Tricks", c2pa_status: "verified" });
        const vid2 = await post("/video/create", { creator_id: c2.id, title: "Hip Hop 30s" });
        setVideoIds([vid1.id, vid2.id]);
    }

    async function start() {
        const s = await post("/session/start", { viewer_id: viewer });
        setSessionId(s.session_id);
    }

    async function watch(videoId, sec, inter = 0, boost = 0) {
        await post("/session/event", { session_id: sessionId, video_id: videoId, seconds_watched: sec, interactions: inter, boost_amount: boost });
        // Attested playback receipt (APR) demo commit
        const nonce = Math.random().toString(36).slice(2);
        const apr = await post("/apr/commit", { window: windowId, session_id: sessionId, video_id: videoId, seconds_watched: sec, nonce });
        setCommitments(prev => [...prev, apr.commitment]);
    }

    async function close() {
        const a = await post(`/session/close?session_id=${sessionId}&platform_match_pool=0.4`, {});
        setAlloc(a);
    }

    async function publishRoot() {
        await post("/apr/publish_root?window=" + windowId, {});
    }

    async function showProofs() {
        const p = await get("/apr/proofs?window=" + windowId);
        alert("Merkle Root: " + p.root + "\nProofs for first leaf: " + JSON.stringify(p.proofs[0], null, 2));
    }

    return (
        <Router>
            <div className="container">
                <h1>Duuck Demo</h1>
                <nav>
                    <ul>
                        <li><Link to="/bounty">Bounty List</Link></li>
                        <li><Link to="/new-bounty">Create New Bounty</Link></li>
                        <li><Link to="/submit-video">Submit Video</Link></li>
                        <li><Link to="/vote">Vote</Link></li>
                        <li><Link to="/results">Results</Link></li>
                    </ul>
                </nav>
                <div className="row">
                    <button className="btn" onClick={seed}>1) Seed Data</button>
                    <button className="btn" onClick={start} disabled={!viewer}>2) Start Session</button>
                    <button className="btn" onClick={() => watch(videoIds[0], 45, 2, 0.5)} disabled={!sessionId}>Watch Vid1</button>
                    <button className="btn" onClick={() => watch(videoIds[1], 30, 1, 0.0)} disabled={!sessionId}>Watch Vid2</button>
                    <button className="btn" onClick={close} disabled={!sessionId}>3) Close & Allocate</button>
                    <button className="btn" onClick={publishRoot}>4) Publish Merkle Root</button>
                    <button className="btn" onClick={showProofs}>Show Proofs</button>
                </div>
                <div className="card" style={{ marginTop: 16 }}>
                    <div><span className="pill">Window</span> {windowId}</div>
                    <div className="small">APR commitments: {commitments.length > 0 ? commitments.join(", ").slice(0, 80) + "…" : "(none)"}</div>
                </div>
                {alloc && (
                    <div className="card" style={{ marginTop: 16 }}>
                        <h2>Transparency Breakdown</h2>
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Creator</th>
                                    <th>Video</th>
                                    <th>Weight</th>
                                    <th>$ Amount</th>
                                    <th>Explain</th>
                                </tr>
                            </thead>
                            <tbody>
                                {alloc.breakdown.map((b, i) => (
                                    <tr key={i}>
                                        <td>{b.creator_id}</td>
                                        <td>{b.video_id}</td>
                                        <td>{b.weight}</td>
                                        <td>${b.amount.toFixed(2)}</td>
                                        <td className="small">cq:{b.explain.cqscore.toFixed(2)} boost:{b.explain.boost}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div>Total Spent Today: ${alloc.total_spent.toFixed(2)}</div>
                        <div className="small">(Includes platform quadratic match pool.)</div>
                    </div>
                )}
                <Routes>
                    <Route path="/bounty" element={<BountyListPage />} />
                    <Route path="/new-bounty" element={<NewBountySubmissionPage />} />
                    <Route path="/submit-video" element={<VideoSubmissionPage />} />
                    <Route path="/vote" element={<VotingPage />} />
                    <Route path="/results" element={<ResultsPage />} />
                </Routes>
            </div>
        </Router>
    );
}