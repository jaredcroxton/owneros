# The CREW Plays and Chain Plays, complete
For the OwnerOS build. This is the full play library from my PerformOS playbook: 46 plays across 11 categories, plus 12 chain plays. A play is a runnable routine: when to use it, the exact prompt to type into Claude Code, what comes back, and the next move. The `intents` line is the keyword list used to match a user's plain words to the play; keep it, it is gold for search or an intent box in the OS.

How the OwnerOS should use these: a PLAYS screen alongside the skill deck. Group by category, searchable by intent words, each play card shows When / Prompt (with copy button) / What you get / Next move / Tip. Chain plays render as a numbered pipeline of skills, each step one crew skill; one project holds the whole chain. Skill names in chains carry the crew- prefix when invoked (for example needs-analyser runs as crew-training-needs-analyser). The prompts assume the CREW is installed and the business is onboarded.

---


## Getting started

### Onboard your business (do this first)

- **When:** Once per business, before anything else. Every skill reads this file forever after.
- **Prompt:** `Let's set up my Crew. Run crew-core-brand-context to onboard my business.`
- **You get:** An 11-question conversation, then one brand file every skill reads. You only do this once.
- **Next:** Start your first play: any build below.
- **Tip:** Have your website open: colours, wording, and offers come faster when you can copy-paste.
- **Intents:** onboard, set up, brand context, start, first time, setup, get started

### Start a new piece of work (a project)

- **When:** Any time you build something new. Every project is kept separately and nothing ever overwrites anything.
- **Prompt:** `New project, call it [name]. [Then say what you want built.]`
- **You get:** A named folder in your Crew's memory holding every record for this piece of work.
- **Next:** When you come back later: the play below.
- **Tip:** Name projects like a folder you would find in a year: client name, product, campaign.
- **Intents:** new project, start a project, begin, new build, new work

### Continue earlier work

- **When:** Whenever you return to something you built before, even months later.
- **Prompt:** `Where were we? List my projects.`
- **You get:** Your projects listed with dates; pick one and the Crew reloads exactly where that work stopped.
- **Next:** Carry on: the Crew now works inside that project.
- **Tip:** Teach your team this habit: continuing? Restore first. New? Just name it and go.
- **Intents:** continue, where were we, resume, pick up, restore, come back, previous

### Switch between businesses

- **When:** You run more than one business (or want a personal brand cabinet).
- **Prompt:** `Switch to [brand name].`
- **You get:** The whole filing cabinet swaps: that brand's identity, projects, and lessons come live.
- **Next:** Switch back any time; everything returns exactly as you left it.
- **Tip:** Finish or save what you are doing before switching; the swap is whole-cabinet.
- **Intents:** switch brand, other business, change business, second brand, multiple businesses

### Teach the Crew a lesson permanently

- **When:** You corrected something and never want to repeat the correction.
- **Prompt:** `Save that as a lesson so it never happens again.`
- **You get:** One line written to that skill's local lessons file, applied at every future start, survives every update.
- **Next:** Nothing: it is permanent from the next run.
- **Tip:** Lessons are per skill and stay on your machine. Product updates never erase them.
- **Intents:** lesson, remember this, never again, correct, fix behaviour, teach


## Sales

### Research a prospect before you call

- **When:** Before any first call, demo, or proposal to a company you do not know well.
- **Prompt:** `New project, call it [client name]. Run crew-sales-lead-research on [company + website/LinkedIn]. I want who they are, what they sell, recent signals, and a conversation angle for [your offer].`
- **You get:** A research brief with a chosen conversation angle, evidence-tagged, nothing invented.
- **Next:** Chain it: 'Now run crew-sales-prospect-brief' then outreach below.
- **Tip:** Paste any links you already have; real inputs beat searches.
- **Intents:** research a company, prospect, lead research, before a meeting, who is this company

### Write the outreach (email or DM)

- **When:** You know who they are; now you need the first touch that gets a reply.
- **Prompt:** `Continuing [client name]. Run crew-sales-outreach-draft: a first-touch email and a LinkedIn DM using the brief's angle. My goal: [book a call / demo].`
- **You get:** Ready-to-send drafts in your voice, built on the research, with follow-up hooks.
- **Next:** Booked? Quote them: the Mobile Quote play. Silent? Follow-up sequence below.
- **Tip:** It reads the research automatically inside the same project; that is the chain working.
- **Intents:** outreach, cold email, first email, linkedin message, contact a lead

### Build a follow-up sequence

- **When:** A lead went quiet, or you want a standing 3 to 5 touch rhythm.
- **Prompt:** `Continuing [client name]. Run crew-sales-follow-up-sequence: [N] touches over [T] weeks, ending with a clean break-up note.`
- **You get:** The full sequence, each touch different (value, proof, nudge), never desperate.
- **Next:** Replies land? Proposal play.
- **Tip:** Ask it to mark each touch with its send date so you can diarise them.
- **Intents:** follow up, sequence, no reply, chase, nurture

### Write a proposal that closes

- **When:** The call went well and they asked for it in writing.
- **Prompt:** `Continuing [client name]. Run crew-sales-proposal-builder: scope [what you'll do], price [your number], timeline [when]. Confirm my numbers back to me before finalising.`
- **You get:** A structured proposal built on everything the project knows, rendered as a proper document.
- **Next:** Send it as a phone-first link instead: the Mobile Quote play.
- **Tip:** Never let it invent a price; it will use your number verbatim and confirm first.
- **Intents:** proposal, quote document, pitch document, scope, offer document

### Send a quote as a link in a text (Mobile Quote)

- **When:** Trades, services, fast-moving deals: the quote they swipe on their phone and accept.
- **Prompt:** `New project, call it [client]-quote. Send my quote as a link: mobile story deck for [client]. The job: [what]. Price: [$X inc GST], includes [a, b, c]. Guarantee: [yours]. Action: Accept or call [number].`
- **You get:** A 9:16 swipe deck: hook, problem, the work, the price huge, guarantee, one thumb-reach button.
- **Next:** They accepted? Invoice workflow under Money.
- **Tip:** The price panel is the hero; give the real number and it lands with a count-up.
- **Intents:** quote, send my quote, phone proposal, text a quote, mobile quote, story deck quote

### Clean up the pipeline / CRM

- **When:** Monthly, or when the pipeline stops being believable.
- **Prompt:** `New project, call it pipeline-[month]. Run crew-sales-pipeline-review on this: [paste your deal list or export]. Which deals are real, which are stale, what needs action this week?`
- **You get:** An honest read: real vs stale, next action per deal, and what the pipeline actually totals.
- **Next:** crew-sales-crm-cleanup for the record-by-record tidy.
- **Tip:** Paste the ugly export as-is; cleaning messy input is the point.
- **Intents:** crm, pipeline review, clean crm, deals list, sales review


## Marketing

### Plan a campaign

- **When:** Anything you are about to promote: an offer, an event, a season.
- **Prompt:** `New project, call it [campaign name]. Run crew-marketing-campaign-plan: goal [bookings/sales/signups], audience [who], budget [$ or none], running [dates]. Give me the angle, the channels, and the week-by-week plan.`
- **You get:** A campaign plan with one clear angle and a channel-by-channel schedule you can actually run.
- **Next:** Feed it onward: social pack, email campaign, landing page review, all in this project.
- **Tip:** One campaign per project keeps every asset and decision together.
- **Intents:** campaign, promotion, launch a promotion, marketing plan, promote

### A week of social posts in one hit

- **When:** Feeding the socials without staring at a blank screen every morning.
- **Prompt:** `Continuing [campaign name] (or: New project, call it socials-[month]). Run crew-marketing-social-post-pack: 7 posts for [platforms], mixing [proof, tips, offer]. My voice, no hashtags soup.`
- **You get:** A dated pack of posts in your brand voice, each with its hook and CTA.
- **Next:** crew-marketing-content-repurpose turns your best one into 5 more formats.
- **Tip:** Give it one real customer story to anchor the week; proof beats cleverness.
- **Intents:** social posts, instagram, facebook posts, content week, posts pack

### Write an email campaign

- **When:** A launch, an offer, or a re-engagement push to your list.
- **Prompt:** `Continuing [campaign name]. Run crew-marketing-email-campaign-builder: [N] emails to [list], goal [action]. Subject lines I would actually open.`
- **You get:** The full sequence with subjects, body copy, and send order, on-voice.
- **Next:** crew-marketing-landing-page-review on wherever those emails point.
- **Tip:** Tell it the ONE action per email; two CTAs is zero CTAs.
- **Intents:** email campaign, newsletter, email sequence, edm

### Review a landing page before you spend on ads

- **When:** Before paid traffic hits any page, or when a page underperforms.
- **Prompt:** `Run crew-marketing-landing-page-review on [URL]. Will it convert for [audience + offer]? Score it, list the fixes in order, and rewrite the weakest call to action.`
- **You get:** A conversion scorecard, ordered fixes, and a rewritten CTA.
- **Next:** Fixes that need a rebuild: crew-web-page-builder under Websites.
- **Tip:** Run it again after the fixes; the score should move or the fix was cosmetic.
- **Intents:** landing page, page review, will this convert, conversion, before ads

### Check anything against your brand voice

- **When:** Anything written by someone else (or an AI) before it ships.
- **Prompt:** `Run crew-marketing-brand-voice-check on this: [paste]. Does it sound like us? Fix what doesn't.`
- **You get:** A verdict with line-by-line fixes against your actual brand file.
- **Next:** Ship it, or send to quality check for the full gate.
- **Tip:** Great for franchisee/staff-written copy; the brand file is the referee.
- **Intents:** brand voice, sounds like us, tone check, voice check, on brand


## Money

### Month-end money summary

- **When:** Every month-end: one page that tells you what happened and what to do.
- **Prompt:** `New project, call it money-[month]. Run crew-finance-monthly-summary. Here are my numbers: [paste or attach revenue, expenses, cash]. Wins, risks, and the three actions for next month.`
- **You get:** A decision-ready one-pager: key numbers, what moved, risks, next actions.
- **Next:** crew-finance-cashflow-brief if cash timing is the worry.
- **Tip:** Same project name pattern every month builds a comparable series.
- **Intents:** month end, monthly summary, how did we do, financial review, monthly report, money summary

### Cashflow health check

- **When:** Cash feels tight, or a big decision (hire, buy, move) is coming.
- **Prompt:** `New project, call it cashflow-check. Run crew-finance-cashflow-brief: [paste balances, incomings, outgoings, dates]. When do I get tight, and what moves the needle?`
- **You get:** The pinch points on a timeline and the levers that actually help.
- **Next:** crew-finance-monthly-summary for the fuller monthly picture.
- **Tip:** Include the LUMPY items (tax, insurance, super); they cause every surprise.
- **Intents:** cashflow, cash position, runway, can i afford, cash brief

### Review expenses for waste

- **When:** Quarterly, or whenever margins feel thinner than they should.
- **Prompt:** `New project, call it expense-review-[quarter]. Run crew-finance-expense-review on: [paste expense export]. Flag waste, duplicates, and what to renegotiate.`
- **You get:** A ranked hit-list: cancel, renegotiate, keep, with the money each returns.
- **Next:** crew-finance-admin-automation to stop the waste recurring.
- **Tip:** Export 3 months, not 1; the quarterly subscriptions hide in month two.
- **Intents:** expenses, spending, subscriptions, costs, cut costs, expense review

### Chase and tidy invoicing

- **When:** Money is owed and the follow-up is awkward or forgotten.
- **Prompt:** `Run crew-finance-invoice-workflow: here's who owes what [paste]. Give me the chase messages (friendly, firm, final) and the rhythm to send them.`
- **You get:** A courteous-but-effective chase sequence and a standing invoicing rhythm.
- **Next:** crew-ops-recurring-task-automation to make the rhythm automatic.
- **Tip:** The 'friendly' first nudge recovers most of it; send it earlier than feels polite.
- **Intents:** invoice, invoicing, get paid, chase payment, overdue

### Plan a finance dashboard

- **When:** You never quite know how the business is doing between month-ends.
- **Prompt:** `New project, call it finance-dashboard. Run crew-finance-finance-dashboard-plan: I decide [pricing, hiring, spend] and I can pull numbers from [Xero/bank/sheets].`
- **You get:** A one-page dashboard plan: the few metrics that matter, sources, and layout a bookkeeper can build.
- **Next:** Hand the plan to whoever owns your books.
- **Tip:** Fewer numbers, watched weekly, beats forty numbers watched never.
- **Intents:** dashboard, numbers to track, kpis, metrics, finance dashboard


## People

### Write a role profile before hiring

- **When:** Before you advertise anything: get the role itself right first.
- **Prompt:** `New project, call it hire-[role]. Run crew-hr-role-profile-builder: we need [role] because [why]. Outcomes I need in 90 days: [list].`
- **You get:** A real role profile: outcomes, responsibilities, must-haves vs nice-to-haves.
- **Next:** Interview guide next, same project.
- **Tip:** Write outcomes, not tasks; you are hiring for results.
- **Intents:** hire, role profile, job description, new position, recruit

### Build an interview guide

- **When:** Interviews are booked and you want signal, not vibes.
- **Prompt:** `Continuing hire-[role]. Run crew-hr-interview-guide from the role profile: scored questions that test the real outcomes, plus red flags.`
- **You get:** A structured guide: questions per outcome, what good sounds like, scoring.
- **Next:** Hired? New-starter onboarding under Training.
- **Tip:** It builds from the role profile automatically inside the project.
- **Intents:** interview, interview questions, hiring questions, assess candidate

### Prepare a hard performance conversation

- **When:** Someone is missing the mark and the conversation cannot wait any longer.
- **Prompt:** `New project, call it perf-[initials]. Run crew-hr-performance-conversation-prep: the situation [facts], what good looks like [standard], history [any prior chats]. Keep it fair and specific.`
- **You get:** A conversation plan: opening lines, evidence, the ask, and where the line is.
- **Next:** crew-hr-employee-communication-draft for the written follow-up.
- **Tip:** Facts and dates in, feelings out; the prep forces the specifics that make it fair.
- **Intents:** performance, difficult conversation, underperforming, staff issue, tough talk

### Summarise a policy so humans read it

- **When:** A dense policy needs to become something staff will actually absorb.
- **Prompt:** `Run crew-hr-policy-summary on this: [paste policy]. One page, plain language, what changes for staff.`
- **You get:** A plain-English one-pager with the do's, don'ts, and who to ask.
- **Next:** crew-docs-policy-document-generator when you need the formal policy itself.
- **Tip:** Ask for a 'what changed' box when it replaces an older version.
- **Intents:** policy, summarise policy, staff handbook, rules summary


## Operations

### Map a process that lives in someone's head

- **When:** A key process exists only as tribal knowledge and it is a risk.
- **Prompt:** `New project, call it process-[name]. Run crew-ops-process-map: I'll describe how [process] works, you turn it into a clear map with owners and handoffs. Here's the messy version: [brain dump].`
- **You get:** A clean step-by-step map with owners, inputs, outputs, and the gaps exposed.
- **Next:** crew-docs-sop-builder turns the map into a trainable SOP.
- **Tip:** Dump it messy; structuring the mess is the skill's whole job.
- **Intents:** process, map a process, how we do things, document process, sop start

### Find what to automate first

- **When:** Everyone is busy but nobody can say where the hours go.
- **Prompt:** `New project, call it automation-review. Run crew-ops-automation-opportunity-review: here's what the team does weekly [list/roles]. Rank what to automate by payoff and ease.`
- **You get:** A ranked automation list: effort, payoff, tool suggestions, quick wins first.
- **Next:** crew-ops-recurring-task-automation to design the top pick.
- **Tip:** Include the annoying small stuff; weekly 20-minute tasks are the compounding wins.
- **Intents:** automate, automation, repetitive, save time, what to automate

### Fix a workflow that keeps breaking

- **When:** The same failure keeps happening and patches have not held.
- **Prompt:** `New project, call it fix-[workflow]. Run crew-ops-workflow-improvement: what breaks [describe], how often, what it costs. Find the root cause, not a patch.`
- **You get:** Root-cause analysis and a redesigned flow with the failure point removed.
- **Next:** crew-docs-sop-builder so the fix becomes the standard.
- **Tip:** Bring 2 or 3 real failure examples; patterns live in the examples.
- **Intents:** workflow, bottleneck, keeps going wrong, improve process, fix process


## Customers

### Triage a messy inbox of tickets

- **When:** Support requests pile up faster than they get sorted.
- **Prompt:** `New project, call it support-triage. Run crew-support-ticket-triage on these: [paste tickets/emails]. Sort by urgency and type, flag the fires, draft the quick wins.`
- **You get:** A sorted queue: what burns now, what batches, drafts for the easy ones.
- **Next:** crew-support-reply-builder for the tricky ones; escalation review for the fires.
- **Tip:** Paste raw; subject lines and rambles are what it is built for.
- **Intents:** tickets, support inbox, triage, customer emails, complaints pile

### Answer a hard customer email

- **When:** The reply that needs to be right the first time.
- **Prompt:** `Run crew-support-reply-builder: here's their message [paste] and the true situation [facts, what you can/can't do]. On-brand, honest, keeps the customer.`
- **You get:** A reply that owns what is yours, fixes what it can, and holds the line kindly.
- **Next:** Pattern behind it? Feedback summary below.
- **Tip:** Give it the uncomfortable truth; honest constraints produce credible replies.
- **Intents:** reply, difficult customer, complaint, angry customer, respond

### Turn feedback into an action list

- **When:** A pile of reviews/surveys and no clear signal.
- **Prompt:** `New project, call it feedback-[period]. Run crew-support-feedback-summary on: [paste reviews/surveys]. Themes, sentiment, and the three fixes that would matter most.`
- **You get:** Themes ranked by frequency and impact, with verbatim quotes as evidence.
- **Next:** Feed the top theme into ops (fix the process) or marketing (amplify the praise).
- **Tip:** Include the raves too; what to protect matters as much as what to fix.
- **Intents:** feedback, reviews, survey results, what customers say, nps

### Build the FAQ that stops repeat questions

- **When:** The same five questions eat your week.
- **Prompt:** `New project, call it faq. Run crew-support-faq-builder: our top questions [list them + your answers, rough is fine]. Customer-friendly wording, grouped sensibly.`
- **You get:** A publishable FAQ set, grouped, in your voice, ready for the website.
- **Next:** crew-support-help-document-generator for the deeper how-to guides.
- **Tip:** Write answers as you would SAY them; it will clean them up without losing you.
- **Intents:** faq, common questions, help page, self service


## Documents

### Turn knowledge into an SOP

- **When:** Any task only one person can do properly.
- **Prompt:** `Continuing process-[name] (or New project, call it sop-[task]). Run crew-docs-sop-builder: audience [who follows it], format [checklist/steps]. Make it impossible to do wrong.`
- **You get:** A clean SOP with steps, checks, screenshots slots, and failure warnings.
- **Next:** crew-docs-training-guide-creator to teach it; compliance check if regulated.
- **Tip:** Test it on the newest person; their confusion marks the missing steps.
- **Intents:** sop, standard operating procedure, how to guide, document a task

### Meeting notes into actions

- **When:** Every meeting that ends with 'someone should...'
- **Prompt:** `Run crew-docs-meeting-notes-to-actions on: [paste notes/transcript]. Actions with owners and dates, decisions made, and what was parked.`
- **You get:** An action register: who, what, when, plus the decision log.
- **Next:** Paste next meeting's notes into the same project; it carries the open items.
- **Tip:** Record the meeting and paste the transcript; nothing beats the raw words.
- **Intents:** meeting notes, minutes, action items, after a meeting

### A client-facing playbook or handover

- **When:** Ending an engagement or systematising how clients work with you.
- **Prompt:** `New project, call it [client]-handover. Run crew-docs-handover-document-writer (or crew-docs-client-playbook-builder): everything they need to run without me: [systems, logins-locations, rhythms, contacts].`
- **You get:** A professional handover/playbook document, rendered beautifully, client-ready.
- **Next:** crew-core-quality-checker before it goes out; it's your reputation in a PDF.
- **Tip:** List where credentials LIVE, never the credentials themselves.
- **Intents:** client playbook, handover, offboarding document, client guide

### Deep research with cited sources (NotebookLM)

- **When:** Big decisions or content that must be grounded in real sources, not vibes.
- **Prompt:** `New project, call it research-[topic]. Use crew-docs-research-notebooklm. Sources: [URLs, PDFs, YouTube links]. Answer, grounded and cited: [your question]. Then generate an audio overview I can listen to.`
- **You get:** Cited answers from YOUR sources plus a podcast-style audio overview (and video, deck, quiz on request), all downloaded into the project.
- **Next:** Feed the findings to a proposal, deck, or learning journey; the research chains.
- **Tip:** One-time setup first (it walks you through 2 commands). Note: sources go to Google's NotebookLM; keep truly sensitive docs out.
- **Intents:** research, deep research, notebooklm, audio overview, study sources, cite sources, podcast from sources


## Training

### Start from nothing: find the real training need

- **When:** Something is off with performance and 'training' is the guess. Start here, not at content.
- **Prompt:** `New project, call it training-[team]. Run crew-training-needs-analyser: the problem I see [describe], who [team], what good looks like [outcome].`
- **You get:** The actual gap (skill, knowledge, process, or motivation) and whether training even fixes it.
- **Next:** If it IS training: module outline, next play. The chain runs in this project.
- **Tip:** Half the time it is not a training problem; this play saves you building the wrong thing.
- **Intents:** training need, skills gap, what training, team can't, performance problem training

### Have a topic? Design the module

- **When:** You know WHAT to teach; this makes it teachable.
- **Prompt:** `Continuing training-[team] (or New project). Run crew-training-module-outline-builder: topic [X], learners [who], time [minutes], outcome: they can [do what] afterwards.`
- **You get:** A structured outline: measurable objectives, Tell-Show-Do-Check flow, timings, activities.
- **Next:** Facilitator guide next; the chain carries everything forward.
- **Tip:** Give a DOING outcome ('they can price a job'), not a knowing one; the whole design hangs off it.
- **Intents:** module outline, design training, training on, course outline, teach my team

### Turn the outline into a run-anywhere session

- **When:** The outline is approved; now anyone on the team should be able to deliver it.
- **Prompt:** `Continuing training-[team]. Run crew-training-facilitator-guide-creator from the approved outline. Then crew-training-learner-workbook-builder for the participant workbook.`
- **You get:** A minute-by-minute guide (say/do/ask scripts, activities, timings) plus the matching workbook.
- **Next:** The showstopper: the play below turns it into the online journey.
- **Tip:** This is the chain at full power: outline feeds guide feeds workbook, no re-explaining.
- **Intents:** facilitator guide, run a session, deliver training, session plan, workbook

### The PowerPoint killer: present it as an online journey

- **When:** Delivery day: replace the deck with a presented journey the room follows.
- **Prompt:** `Continuing training-[team]. Run crew-web-learning-experience: activate the programme into a presented journey. Solo mode, my laptop, [venue/date].`
- **You get:** A full presented experience: calm slides, presenter notes and clocks, whiteboard capture, phone remote, editable in place. Covers the WHOLE guide.
- **Next:** After the session: export the recap; assessment designer if you need a check.
- **Tip:** Rehearse mode (?rehearse=1) runs the clocks without recording; do one pass the night before.
- **Intents:** powerpoint killer, learning journey, present training, online training, training experience

### Onboard a new starter properly

- **When:** Someone starts soon and you want their first 90 days deliberate.
- **Prompt:** `New project, call it onboard-[name/role]. Run crew-training-onboarding-programme-builder from the role profile: start date [when], buddy [who], the outcomes from the hire project.`
- **You get:** A phased programme: pre-start through first quarter, checklists, manager touchpoints, gates.
- **Next:** crew-training-coaching-conversation-guide for the manager's check-ins.
- **Tip:** Chain it from the hire-[role] project and it inherits the role's outcomes automatically.
- **Intents:** onboarding, new starter, first week, new employee, induction


## Websites & decks

### A clean premium website page

- **When:** A page that has to look like you paid a studio.
- **Prompt:** `New project, call it [site name]. Run crew-web-page-builder: a [landing page/site] for [offer], sections: [hero, proof, offer, CTA]. My brand, real copy from: [paste rough copy].`
- **You get:** A single-file premium page in your brand, with the design gates run before you see it.
- **Next:** Landing-page review before ads; deploy when happy.
- **Tip:** Give real copy, even rough; it elevates yours instead of writing lorem-ipsum-with-confidence.
- **Intents:** website, landing page build, web page, site for, homepage

### A laptop/projector slide deck

- **When:** Presenting in a room or on a call.
- **Prompt:** `New project, call it deck-[topic]. Run crew-web-slide-deck-builder: [N] slides, purpose [pitch/update/training], content: [outline or paste]. My brand.`
- **You get:** A single-file HTML deck: arrows, dots, keyboard, swipe, animated, zero dependencies.
- **Next:** Phone-first version: the mobile deck play.
- **Tip:** One idea per slide; it will push back if you cram, let it.
- **Intents:** slide deck, presentation, pitch deck, slides, deck for meeting

### A phone-first story deck (9:16)

- **When:** Sent as a link, read on a phone: announcements, offers, mini-pitches.
- **Prompt:** `New project, call it story-[topic]. Run crew-web-slide-deck-mobile: a vertical story deck about [X]. Panels: [hook, 3 points, CTA]. My brand.`
- **You get:** Full-screen swipe panels with reels-native type and one signature moment.
- **Next:** For priced quotes use the Mobile Quote play (same engine, money template).
- **Tip:** It will show you the panel map before building; that is your moment to cut.
- **Intents:** mobile deck, vertical deck, story deck, reel style deck, phone deck

### A cinematic scroll experience

- **When:** The launch moment that needs jaws on floors: product, property, announcement.
- **Prompt:** `New project, call it [name]-cinematic. Run crew-web-fly-through-builder (or crew-web-cinematic-build): journey [start to arrival], assets [KIE key / my footage / generate prompts for me].`
- **You get:** A scroll-driven cinematic descent ending at your arrival payoff, engineered mobile-safe.
- **Next:** The design gates run automatically; deploy and send the link.
- **Tip:** No footage? It writes the generation prompts for whatever video tool you use.
- **Intents:** cinematic, scroll site, fly through, immersive, wow website, launch site


## Quality

### Gate anything before it ships

- **When:** Anything important: proposal, page, policy, deck, before a client sees it.
- **Prompt:** `Run crew-core-quality-checker: here's the work [paste/point] and the brief [what it had to do]. Ship, fix, or stop?`
- **You get:** A verdict (Ship / Ship with fixes / Do not ship) with every issue graded and its exact fix.
- **Next:** Apply fixes, re-gate if it was 'Do not ship'.
- **Tip:** The design skills (packs 12-14) are consulted AUTOMATICALLY by every build skill; you never invoke them. This gate is the one you call yourself.
- **Intents:** quality check, review before sending, is this ready, check my work, qa


---

# Chain plays

Several plays, one project, each step feeding the next through the filing cabinet handoffs.

### Chain 01: Learning design, end to end

1. `needs-analyser`
2. `module-outline-builder`
3. `facilitator-guide-creator`
4. `learner-workbook-builder`
5. `assessment-designer`
6. `web-learning-experience`

**Note:** Start wherever you are: unsure what is wrong = step 1. Have a topic = step 2. Guide exists = jump to the journey.

### Chain 02: Quote to cash

1. `sales-lead-research`
2. `sales-outreach-draft`
3. `slide-deck-mobile (Mobile Quote)`
4. `finance-invoice-workflow`

**Note:** One project per client carries everything: research feeds outreach feeds the quote feeds the invoice.

### Chain 03: Campaign launch

1. `marketing-campaign-plan`
2. `marketing-social-post-pack`
3. `marketing-email-campaign-builder`
4. `marketing-landing-page-review`

**Note:** Plan once; every asset inherits the angle inside the same project.

### Chain 04: New hire, day zero to day 90

1. `hr-role-profile-builder`
2. `hr-interview-guide`
3. `training-onboarding-programme-builder`
4. `training-coaching-conversation-guide`

**Note:** The role's outcomes flow through interviews into onboarding automatically.

### Chain 05: Research to deliverable

1. `docs-research-notebooklm`
2. `sales-proposal-builder / web-slide-deck-builder`
3. `core-quality-checker`

**Note:** Grounded, cited research feeds whatever you build; the gate checks the claims survived.

### Chain 06: Knowledge capture

1. `ops-process-map`
2. `docs-sop-builder`
3. `docs-training-guide-creator`
4. `web-learning-experience`

**Note:** Tribal knowledge becomes a map, the map becomes an SOP, the SOP becomes training anyone can run.

### Chain 07: The monthly money hour

1. `finance-monthly-summary`
2. `finance-cashflow-brief`
3. `finance-expense-review`
4. `finance-invoice-workflow`

**Note:** One sitting each month: what happened, where cash pinches, what to cut, who to chase.

### Chain 08: Support intelligence loop

1. `support-ticket-triage`
2. `support-feedback-summary`
3. `support-faq-builder`
4. `ops-workflow-improvement`

**Note:** Complaints become themes, themes become self-service and process fixes. The inbox shrinks itself.

### Chain 09: Content engine

1. `marketing-brand-voice-check`
2. `marketing-content-repurpose`
3. `marketing-social-post-pack`
4. `marketing-email-campaign-builder`

**Note:** One good piece, voice-checked, becomes a fortnight of content across every channel.

### Chain 10: Website launch

1. `web-page-builder`
2. `marketing-seo-page-builder`
3. `marketing-landing-page-review`
4. `core-quality-checker`

**Note:** Build it, make it findable, make it convert, gate it. Then deploy.

### Chain 11: Client delivery, start to finish

1. `sales-prospect-brief`
2. `sales-proposal-builder`
3. `docs-handover-document-writer`
4. `docs-client-playbook-builder`

**Note:** The whole engagement lives in one project, ending with a handover that makes you look like a firm.

### Chain 12: Performance turnaround

1. `hr-performance-conversation-prep`
2. `hr-employee-communication-draft`
3. `training-coaching-conversation-guide`
4. `training-skill-gap-mapper`

**Note:** From the hard conversation to a fair, documented development plan.
