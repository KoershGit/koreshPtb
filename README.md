# koreshPtb
---
As described in (https://github.com/bangxiangyong/agentMET4FOF/tree/72af6a3795b757705fa25d92eb997e9628a841cc) create a virtual Python environment (*venv*) activate it, install numpy, install *agentMET4FOF* from PyPI.org.
After that add the folder ptbTestProject to your vitual environment directory\agentMET4FOF_venv and run the following in your virtual environment:

```shell
(agentMET4FOF_venv) $ python
>>>from ptbTestProject import ptbTestKoresh
>>>ptbTestKoresh.main()
...
```

Now you can visit `http://127.0.0.1:8050/` with any Browser and watch the noisy SineGenerator agent together with its filtered signal, a pulseGenerator and a schockGaussianGenerator you just spawned. Also, you can find figures of the result in Fig_Results.
