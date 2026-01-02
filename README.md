<p align="center">
<h1 align="center"><strong>When Reasoning Meets Its Laws</strong></h1>
  <p align="center">
    <a href='https://jyzhang1208.github.io/' target='_blank'>Junyu Zhang </a><sup><img src="assets/uiuc.svg" align="center" width=0.8% >∗</sup>&emsp;
    <a href='https://yifansun99.github.io/' target='_blank'>Yifan Sun </a><sup><img src="assets/uiuc.svg" align="center" width=0.8% >∗</sup>&emsp;
    <a href='https://dragondescentzerotsu.github.io/' target='_blank'>Tianang Leng </a><sup><img src="assets/upenn.png" align="center" width=0.9% >∗</sup>&emsp;
    <a href='https://jy-evangeline.github.io/' target='_blank'>Jingyan Shen </a><sup><img src="assets/nyu.png" align="center" width=1.0% >∗</sup>&emsp;
    <br>
    <a href='https://www.mit.edu/~ziyinl/' target='_blank'>Liu Ziyin </a><sup><img src="assets/mit.png" align="center" width=1.1% style="margin-right:0.1em;"><img src="assets/ntt.png" align="center" width=1.3% >&#8224</sup>&emsp;
    <a href='https://pliang279.github.io/' target='_blank'>Paul Pu Liang </a><sup><img src="assets/mit.png" align="center" width=1.1%>&#8224</sup>&emsp;
    <a href='https://huan-zhang.com/' target='_blank'>Huan Zhang </a><sup><img src="assets/uiuc.svg" align="center" width=0.8% >&#8224</sup>&emsp;
    <br>
    <sup><img src="assets/uiuc.svg" align="center" width=0.8% ></sup> University of Illinois Urbana-Champaign <sup>
    &emsp;&emsp;<img src="assets/mit.png" align="center" width=1.1%></sup> Massachusetts Institute of Technology
    <br>
    <sup>&emsp;&emsp;<img src="assets/upenn.png" align="center" width=0.9% ></sup> University of Pennsylvania
    <sup>&emsp;&emsp;<img src="assets/nyu.png" align="center" width=1.0% ></sup> New York University
    <sup>&emsp;&emsp;<img src="assets/ntt.png" align="center" width=1.3% ></sup> NTT Research
    <br>
    <sup>∗</sup> Equal contribution&emsp;<sup>&#8224;</sup> Equal mentorship
    <br>
  </p>
</p>

</p>
<p align="center">
  <a href='https://arxiv.org/abs/2512.17901'>
    <img src='https://img.shields.io/badge/Arxiv-2512.17901-A42C25?style=flat&logo=arXiv&logoColor=A42C25'></a>
  <a href='https://arxiv.org/pdf/2512.17901'>
    <img src='https://img.shields.io/badge/Paper-PDF-yellow?style=flat&logo=arXiv&logoColor=yellow'></a>
  <a href='https://lore-project.github.io/'>
    <img src='https://img.shields.io/badge/Project-Page-green?style=flat&logo=Google%20chrome&logoColor=green'></a>
  <a href='https://github.com/ASTRAL-Group/LoRe'>
    <img src='https://img.shields.io/badge/GitHub-Code-black?style=flat&logo=github&logoColor=white'></a>
</p>

## 🚀 News

- **[2025/11]** LoRe was selected as a **Best Paper Nomination** at the NeurIPS 2025 Workshop on Efficient Reasoning.

## 🏠 About
<div style="text-align: center;">
    <img src="assets/teaser.png" width=100% >
</div>

Despite the superior performance of Large Reasoning Models (LRMs), their reasoning behaviors are often counterintuitive, leading to suboptimal reasoning capabilities.
<div style="text-align: center;">
    <img src="assets/framework.png" width=100% >
</div>

We present the Laws of Reasoning (LoRe), a unified framework that characterizes intrinsic reasoning patterns in LRMs. LoRe introduces the *compute law* with the supplementary *accuracy law*, examined through two properties: *monotonicity* and *compositionality*. LoRe-Bench, our proposed benchmark, systematically measures these two tractable properties for LRMs. To address the compositionality gap observed in existing models, we develop an effective finetuning approach that enforces compute-law compositionality.

As a comprehensive study from theoretical hypotheses to empirical validation, we advance a theoretical perspective grounded in human reasoning for improving reasoning in LRMs. We hope LoRe can inspire more potential strategies that guide models toward their optimal paradigms of thinking.

🚧 **Code release under construction — stay tuned!** 🚧

## Model Zoo

Our SFT-Compo models are available on [Hugging Face](https://huggingface.co/LoRe-Team) 🤗.

| Model    | Size | SFT Data                                                                                              | Checkpoint                                                                                        |
|----------|------|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| SFT-Compo | 1.5B  | [deepscaler-14b-min](LLaMA-Factory/data/deepscaler-14b-min.json)  | [SFT-Compo-Distill-Qwen-1.5B](https://huggingface.co/LoRe-Team/SFT-Compo-Distill-Qwen-1.5B)       |
| SFT-Compo | 7B  | [deepscaler-14b-min](LLaMA-Factory/data/deepscaler-14b-min.json)  | [SFT-Compo-Distill-Qwen-7B](https://huggingface.co/LoRe-Team/SFT-Compo-Distill-Qwen-7B)     |
| SFT-Compo | 8B   | [deepscaler-14b-min](LLaMA-Factory/data/deepscaler-14b-min.json) | [SFT-Compo-Distill-Llama-8B](https://huggingface.co/LoRe-Team/SFT-Compo-Distill-Llama-8B)   |


## Contact
If you have any questions related to the code or the paper, feel free to email Junyu Zhang (`junyuz6@illinois.edu`).

## Citation

If you find our work useful in your research, please consider citing LoRe:

```
@article{LoRe25,
  title={When Reasoning Meets Its Laws},
  author={Zhang, Junyu and Sun, Yifan and Leng, Tianang and Shen, Jingyan and Ziyin, Liu and Liang, Paul Pu and Zhang, Huan},
  journal={arXiv preprint arXiv:2512.17901},
  year={2025}
}
```

