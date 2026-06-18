# Meeting Transcript - 2026-06-15T15:29:30.569729+00:00

- Session ID: `596d9213-6f74-4b57-918c-f6a0242074fb`
- Status: `summarized`
- Started: 2026-06-15T15:29:30.569729+00:00
- Ended: 2026-06-15T16:02:13.288947+00:00
- Audio: `/home/arturka/Documents/Projects/VSCode_projects/meeting-copilot-mvp/backend/data/recordings/596d9213-6f74-4b57-918c-f6a0242074fb-6490be0cfa1a42798feb89535d88a539.wav`

## Transcript

**Arthur:** ㅎㅎㅎㅎㅎㅎㅎ  
今日はRush home摘birdskyの演出を流れる予告です。  
それらはまた、熱帯インタビューを入力して対策とかbased starring、愛犬シューティングとか Spring 응chin featづけられる場合もありますが、ASMRイベントよりもア 날トラウンにはいかに対応してもできるか、なんか無用ですが、やっぱり他のイベントそりゃあ無理なんで、そんなこと言うから突然、続けて放送させたいんですけどね、お待たせしました。お待たせしました。

私はエレクトリカルエンジニアとして4年間、PCBAのブリングアップ、ヴァリデーション、ディバッギングなどのハンズオンな経験を持っており、前のエルマンクでのロールポジションで、多くは高パワーコンバーターと、シンプルなSTM32ベースのエンベロープシステムを使っています. And on a typical project, I had 5 to 10 boards, each with several iterations, so I went through a significant number of bring up and validation cycles. And that's why, when I just saw this position at Humanoid, it stood out to me, because this is kind of work where I can do best.

Okay. Great. So, if it's useful, I'd be happy to walk you through one of my projects, or maybe I can describe my approach to bring up and validation.

**Interviewer:** Perfect. I love it. Go ahead.

**Arthur:** I can start with one of the projects I worked on, and even proud of. It was a very compact 500-watt synchronous rectifier, and it was a 4-layer board, about 25 by 25 millimeters, which is like almost 1 inch, 1 by 1 inch—just a pocket-sized rectifier. The main challenge on this project was achieving reliable high-power operation within such a small PCB area. Most of the issues were related to PCB layout. As I remember, it was voltage ringing caused by capacitor placement: the caps were too far from the MOSFETs, creating a big current loop that behaved like an antenna. I moved these capacitors closer to the MOSFETs and eliminated the voltage ringing. Another problem was thermal management—the board was heating up a lot. I fixed that by increasing the copper area as much as I could, and eventually the thermal behavior was acceptable. Recently, I even found a 3D model of this board; I can show you if needed.

**Interviewer:** Sure. So it sounds like you designed the board initially, or did you make a change to it?

**Arthur:** The schematics weren't mine; they were from another engineer, but I designed the board. There were a few versions for different power levels—two kilowatt, one kilowatt, and 500 watt. I designed everything, but I was especially interested in and proud of the really compact 500 W board.

**Interviewer:** Did you notice different types of problems between the 500 W and 2 kW levels? Was that a big enough power change to change the design characteristics?

**Arthur:** I don't remember exact details for 2K and 1K, but the number of problems increased as the board became more compact. Even on compact boards you can only get your capacitors so close to the bus path—that causes issues, and I thought it was related to higher frequency operation.

**Interviewer:** Okay. Could you walk me through your approach for testing? It sounds like you designed the board, brought it up, and made changes. Did you do any end-of-line functional test design for these boards? How many did you make—can you tell me about volume?

**Arthur:** I usually worked with EVT and DVT tests. I wasn't responsible for PVT because after DVT the boards went to another office where other engineers tested them. Would I be comfortable doing PVT? Absolutely—I understand how it works. Because I wasn't responsible for PVT, I didn't build fully automatic fixtures, but I can learn to build them.

My typical bring-up and validation process: I bring up a board in stages and before powering it I prepare several things—the board itself, PCB layout, schematics, bill of materials, design specifications, and important datasheets for electrical components. I set up lab equipment: oscilloscopes, multimeters, a current-limited bench supply, a programmer, and any adapters to communicate with the board. Then I do basic safety checks: visual inspection, check for shorts (especially rail-to-ground), then power the board from a current-limited supply while monitoring current draw, power rails, and power sequencing. If it's a power board, I also watch thermal behavior with a thermal camera.

Once electrical safety looks good, I move to functional blocks—clocks, programming the microcontroller and basic firmware, communication interfaces, sensors, loads, and eventually the high-power part of the board. Throughout the process I record and document everything: measurements, failures, fixes—and then turn that into a systematic and repeatable test procedure.

**Interviewer:** Oh, great. That sounds really familiar—like you've done this before. Can I ask you some questions about electrical engineering fundamentals with a slideshow?

**Arthur:** Yeah, sure.

**Interviewer:** Is that cool? Okay. Get into it. I'm going to make you a co-editorator. So if you want to... it's not working. Okay, go present.

**Arthur:** Oh, okay. I can't draw?

**Interviewer:** I can draw for you if you want. You can go ahead and ask me any questions or tell me what you want to know.

**Arthur:** Okay, yeah.

**Interviewer:** Do we know a voltage drop on the diode? What do you think it should be?

**Arthur:** Well, one and a half volts maybe? Or less? Probably less—could be like 0.7 or 0.8.

**Interviewer:** Cool. Let's do 0.7.

**Arthur:** 0.7 volts dropped across each diode, good. So they're like a 1N1148 or something signal diode.

**Interviewer:** Can I take my pen?

**Arthur:** Sure, sure.

**Interviewer:** And what I might do is reduce the case—two diodes instead of four. By the way, do we know what the load is?

**Arthur:** No, we can assume. It looks like a resistor, right?

**Interviewer:** Yeah. We can call it R and give it a value if you want.

**Arthur:** Okay. I'm sure I could do it in my mind; I didn't do it for a while. I'll say around 16 volts.

**Interviewer:** Tell me how you're getting that number.

**Arthur:** I counted—we have a few voltage supplies. I counted current through this resistor from each of them, summed these currents, and multiplied by resistance. That's how I got the voltage on the resistor.

**Interviewer:** If you had this circuit going into, say, an op-amp, then it would work because the op-amp forces that node to a set voltage. If you have a summing junction in an op-amp, you'd sum currents and the op-amp enforces the node voltage. But this circuit has no op-amp—there's no other current into or out of that junction, only currents through the load to ground from 5.8 V and from 12 V. The 12 V flows down and gives you 11.3 V at that node (12 minus 0.7). Once you have 11.3 V there, current won't flow from 5.8 V to 11.3 V because the diode will block it.

**Arthur:** Oh, right. Yeah—it's going to get blocked. I think I was thinking of an op-amp summing junction where the op-amp forces the node and supplies current. Maybe in that case you'd have an independent resistor for each input into the summing node. I understand how the previous picture should be.

**Interviewer:** So are you familiar with this type of circuit implementation? Have you seen it or used it in practice? Can you think of a reason to use a circuit like this?

**Arthur:** I haven't used it much, but let me think quickly. We could use this kind of circuitry if we need to switch which supply powers the load—say the load is normally on 12 V, but if 12 V is absent a lower voltage like 9 V or 5.8 V could supply it through a diode. If the higher voltage is present, it will forward-bias and close the other diode, giving the higher voltage to the load (minus the diode drop). It could be used with a wall-powered supply and a backup battery, for instance—a diode OR-ing scheme to choose the highest available supply.

**Interviewer:** Alright. I've got a hard stop in six minutes. Thank you very much. Do you have any questions for me about the role?

**Arthur:** Yes—what does the bring up and validation process in your team look like today?

**Interviewer:** Right now a designer does the kind of process you walked through. We do some manual recording of data at the design-notebook level—record intended design, get parts in, turn them on, record performance and any changes. If there's a bug, we'll try a rework: component change, wire cut and jump, or additional assembly instructions. We might fab another batch with the fixes and revalidate the first article. Many of our boards have microcontrollers, so we program them and include a functional test at that step. Once design is stabilized, we want to serialize and track boards with their test data. A lot of the work becomes automation and scripting for data collection and storing it into a database. Do you have experience with that workflow?

**Arthur:** With what exactly?

**Interviewer:** Working with the database part—scripting test executables and writing data into a database.

**Arthur:** I usually used CSV files to keep data. That's how it was done at my previous role.

**Interviewer:** Another question: as an electrical test engineer, do you own end-to-end bring up and validation? There's also a lead electrical test engineer role—would that be your supervisor?

**Arthur:** Most likely. In this case we're pretty flat. The lead scopes electrical test engineering work for the team and interfaces as a representative—deciding how we do it, which test houses we use. The engineering role executes day-to-day with design engineers—less management. The lead would be more for a larger team when we grow. You might report to the lead or to me.

**Arthur:** If you decide to call me for a practical interview on site, what should I expect?

**Interviewer:** More of the same—we'd go over circuits, talk about how they should work, show fundamental knowledge of electronics. Some power questions, strategies for testing firmware functions and analog signals. We might present a circuit that doesn't work as intended and ask you to determine what's wrong—identify responsible components or signals. We'll also talk about databasing and automation, scripting and automation.

**Arthur:** Okay, thank you so much.

**Interviewer:** Sorry I'm running out of time. I can take a couple minutes if you have more questions, but otherwise I'm good. Although I am curious—can you give me a quick summary of what you're doing now?

**Arthur:** Absolutely. When I moved to the US, a friend who owns a company doing AI-based authentication of historical paintings invited me to help build AI tools. It sounded interesting—a chance to learn modern computer vision and a different problem-solving perspective. After a few years I want to return to hardware because I miss hands-on work and electrical engineering is my core strength. My current role gave me a broader point of view from software, so now I have a broader perspective across hardware and software.

**Interviewer:** Cool. Yeah, it's neat to have very different tasks. Well, good talking with you, Arthur—be well. I think Katie may be the one following up. Katie?

**Arthur:** Thank you so much. Take care.

**Interviewer:** Yeah, you too. Bye.

**Arthur:** Bye.
