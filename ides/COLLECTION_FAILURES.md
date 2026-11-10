# Collection failures

**0 quarantined; 285 retrying.** Generated from the saved JSON histories, not just the latest workflow run.

After **5 consecutive identical collection failures**, an unchanged record is quarantined: its missing hashes remain unavailable, but it no longer keeps collection jobs queued. Errors are not evidence of a verified artifact. Changed metadata or a new installer checksum can create fresh work. Quarantined checksum failures can also recover through a successful lightweight checksum probe; failed or budget-limited probes do not requeue quarantined records.

Counters are per completed collection attempt, not individual HTTP retries. Histories predating retry tracking start at zero; their earlier failure counts are unknown. Budget limits, interruptions, and infrastructure/safety stops do not consume the allowance.

To explicitly retry one product, run `python -m jetbrains_hashes sync --product CODE --retry-quarantined`, or enable `retry_quarantined` when dispatching the update workflow. This resets only quarantined records and preserves captured hashes. [Manual verification instructions](../MANUAL_VERIFICATION.md).

## DataGrip (`DG`)

[Product table](DG.md) | [JSON history](../data/DG.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025.3.5.1 | 253.31033.213 | release | `macM1` | `944d1bf2cdfb9811c9eded221df2925bff6fa44f7977ffb0a6322091c18372bf` | Retrying | 1/5 | 2026-11-10T20:06:11.000768+00:00 | application: Bundle build mismatch: API says 253.31033.213, bundle says 253.31033.21; refusing to attribute this executable to the wrong build |
| 2025.3.5.1 | 253.31033.213 | release | `mac` | `1644cae61bb71a5a31cf3940b972542371b9c3ce18bf3218b5f6b487a843679c` | Retrying | 1/5 | 2026-11-10T20:06:18.944510+00:00 | application: Bundle build mismatch: API says 253.31033.213, bundle says 253.31033.21; refusing to attribute this executable to the wrong build |
| 2016.3.1 | 163.9735.5 | release | `mac` | `9a1abde45c59cdde3ef884a8cb879fdaeb8899e822120a392890f0038fe94ecf` | Retrying | 1/5 | 2026-11-10T20:06:23.332195+00:00 | application: Bundle build mismatch: API says 163.9735.5, bundle says DB-163.9735.6; refusing to attribute this executable to the wrong build |

## DataSpell (`DS`)

[Product table](DS.md) | [JSON history](../data/DS.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025.2.4 | 252.28539.109 | release | `macM1` | `7e24ea16aac493513782572d1f3a1d84d61fd8dae64f56d4099fb93fb08fbfcc` | Retrying | 1/5 | 2026-11-10T20:18:19.019437+00:00 | application: Bundle build mismatch: API says 252.28539.109, bundle says 252.28539.155; refusing to attribute this executable to the wrong build |
| 2025.2.4 | 252.28539.109 | release | `mac` | `c43df917d98e01a07ecd2032524788c46deffe1b025fcf60463cd79eaa84a0f9` | Retrying | 1/5 | 2026-11-10T20:18:42.877962+00:00 | application: Bundle build mismatch: API says 252.28539.109, bundle says 252.28539.155; refusing to attribute this executable to the wrong build |

## IntelliJ IDEA Community Edition (`IIC`)

[Product table](IIC.md) | [JSON history](../data/IIC.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11.0.2 | 111.277 | release | `mac` | `a56abc799d5141b0c1d3234a97e6a42f53b97de2721aa943f7b2b8478e3c632d` | Retrying | 1/5 | 2026-11-10T20:10:49.529272+00:00 | application: Invalid application metadata: unexpected key at line 10 |

## MPS (`MPS`)

[Product table](MPS.md) | [JSON history](../data/MPS.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026.2-RC2 | 262.11879.672 | eap | `macM1` | `d5e23bea45087d907c397019782b160f2b4f0772bd40f2f004ff5f1be5411287` | Retrying | 0/5 | 2026-11-09T01:20:36.270641+00:00 | application: Invalid application metadata: Invalid file |
| 2026.2-RC1 | 262.10968.569 | eap | `macM1` | `d6722c2b87eaa339381fcd3dd0b3f24e223002b1332f24e8bf5a4f0708dd8c3d` | Retrying | 0/5 | 2026-11-09T01:23:15.101712+00:00 | application: Invalid application metadata: Invalid file |
| 2026.2-EAP1 | 262.9437.166 | eap | `macM1` | `a2d8254edfc93db8cad9adf4db8b0a47d1cb7240965d449115616e6868c453a5` | Retrying | 0/5 | 2026-11-09T01:25:02.588399+00:00 | application: Invalid application metadata: Invalid file |
| 2026.2 | 262.11879.701 | release | `macM1` | `3bd01adf7cf04c51e6b3478a7f1370af7df511012ed7b87902755ad0e2806cc5` | Retrying | 0/5 | 2026-11-09T15:59:01.452119+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1.2 | 261.27258.1085 | release | `macM1` | `d3097f8397da7e6409e01eaa5760d4f800440aaf90ac591fddf5d8ab0dcb79a7` | Retrying | 0/5 | 2026-11-09T01:21:10.088637+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1.2 | 261.27258.1085 | release | `mac` | `5eaecbe04607409a2a467346c5c18b814119c6bb28236d6ebdcef5d3cc283dcd` | Retrying | 0/5 | 2026-11-09T01:21:46.504530+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1.1 | 261.25134.877 | release | `macM1` | `b9170dce0b47f55513ced9f81614064043ead0a5eef52aaf9487cf04fbd78c9b` | Retrying | 0/5 | 2026-11-09T01:23:26.330749+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1.1 | 261.25134.877 | release | `mac` | `817e93a2a9637802efdb3a24fa8dfee06345c13f40466c74a51a376bcfe3aae2` | Retrying | 0/5 | 2026-11-09T01:23:38.478747+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1-RC1 | 261.24374.603 | eap | `macM1` | `07f9a649086b7594909f14a95870d420d9e3334fa4576be5e8288f1ec403a1d1` | Retrying | 0/5 | 2026-11-09T01:26:53.674238+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1-RC1 | 261.24374.603 | eap | `mac` | `269aa48c0ad33412c3a84aea0db97f453923a0131ed67a3b8f1afa2952eb51dd` | Retrying | 0/5 | 2026-11-09T07:40:10.339424+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1-EAP1 | 261.23567.257 | eap | `macM1` | `b94603008e541b83e73e59d5cf20a791471e082f3ead9139869e0bf8db566ec9` | Retrying | 0/5 | 2026-11-09T07:40:35.158203+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1-EAP1 | 261.23567.257 | eap | `mac` | `0a7beaceac60ade9db7a5a3023b553f5277dbdf33f2c2b248f34310d620ce96a` | Retrying | 0/5 | 2026-11-09T07:41:00.880053+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1 | 261.25134.779 | release | `macM1` | `e55b4f4b6ebfbc229afa67c30102a077dc7903e0aabf7f4acfed842a482e97e2` | Retrying | 0/5 | 2026-11-09T01:26:29.377367+00:00 | application: Invalid application metadata: Invalid file |
| 2026.1 | 261.25134.779 | release | `mac` | `04564d1e81a3efee030ec12a2f9c7b25f5a057dd77df0fd6f9ed68c29cec2710` | Retrying | 0/5 | 2026-11-09T01:26:41.674123+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.3 | 253.33813.547 | release | `macM1` | `fae4559acce0baab24390f89cc0e2b8546b854e93c4396a917d3b932f08d3e3d` | Retrying | 0/5 | 2026-11-09T01:21:57.490683+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.3 | 253.33813.547 | release | `mac` | `5285500322ec4e9bdbebae5fb298f072088d7421eab408b26b9613c5ca68c78d` | Retrying | 0/5 | 2026-11-09T01:22:11.681170+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.2 | 253.29346.541 | release | `macM1` | `7cde50cef01d52f2c883f6af79e7cb7af079841eed4e867247913323491a8067` | Retrying | 0/5 | 2026-11-09T01:23:51.484710+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.2 | 253.29346.541 | release | `mac` | `ebf5725cfb0ec695a72e845fffee430cbb8c959bb156b546e82566496cbbbbdf` | Retrying | 0/5 | 2026-11-09T01:24:03.286737+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.1 | 253.29346.537 | release | `macM1` | `15b6250fb04ab90438887d46e5d793cf6549d25980c2692ee9a008e1c7b437fc` | Retrying | 0/5 | 2026-11-09T01:25:13.597322+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3.1 | 253.29346.537 | release | `mac` | `69264b3306addf5625edbd4b224e5d041aa77071ebf828a9d563d98688d02db1` | Retrying | 0/5 | 2026-11-09T01:25:26.463921+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-RC1 | 253.28294.372 | eap | `macM1` | `06b83cec1e70a468ba3d8cdcf2fc6851af7ffdd02f46704471aa97ec99158dfe` | Retrying | 0/5 | 2026-11-09T07:45:31.698968+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-RC1 | 253.28294.372 | eap | `mac` | `45c22988c57779b34366ad40a296355b5cf37bd29941564a770378adad93a71d` | Retrying | 0/5 | 2026-11-09T07:45:54.412335+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-EAP2 | 253.28294.300 | eap | `macM1` | `2eb45698d5580f427e2c93fb82cc1443705731efd334c980ec1f8a2570064d40` | Retrying | 0/5 | 2026-11-09T07:46:17.601337+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-EAP2 | 253.28294.300 | eap | `mac` | `18fdc5ef8a2a5eee33440eb6541ebbd907e1fcc8e9eeb8bb4015d7e6ceadd167` | Retrying | 0/5 | 2026-11-09T07:46:41.544126+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-EAP1 | 253.27864.84 | eap | `macM1` | `246002a7057e6aa9359ffe338cfccde2e22be825734016ed345fef8c668e756c` | Retrying | 0/5 | 2026-11-09T07:47:06.647195+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3-EAP1 | 253.27864.84 | eap | `mac` | `78ba6aa4112e5bf41aa6b33befc4a8599dfe02d2c803deea98967e5985f49f8b` | Retrying | 0/5 | 2026-11-09T07:50:56.366527+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3 | 253.28294.432 | release | `macM1` | `dc79c41ce851448f4862306173914eee1e63e230410ed65356498efd2d5f0444` | Retrying | 0/5 | 2026-11-09T07:44:36.355714+00:00 | application: Invalid application metadata: Invalid file |
| 2025.3 | 253.28294.432 | release | `mac` | `c216008ca905efd9ab9271df9599ef38ecb66cba2c61482e7a56434ae3eddee6` | Retrying | 0/5 | 2026-11-09T07:45:07.506093+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.5 | 252.28539.674 | release | `macM1` | `9f9dd0592c306649388c53664e2443c86b215633842b56cb006412f1be68d95c` | Retrying | 0/5 | 2026-11-09T01:22:24.830983+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.5 | 252.28539.674 | release | `mac` | `9a041da0dd474dd2c7ad5c0bede31efb357b84e541919c0c290b31607450b92b` | Retrying | 0/5 | 2026-11-09T01:22:38.255581+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.4 | 252.28539.667 | release | `macM1` | `c54bad3d94d0646451779c9dafd417f49f23cc07d911136e3cbdd18697f3bb39` | Retrying | 0/5 | 2026-11-09T01:24:14.763831+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.4 | 252.28539.667 | release | `mac` | `658b081a86cb0bfdd84a2e4cc46faa4431bf0a54e76160c7f271e8494e5ff56e` | Retrying | 0/5 | 2026-11-09T01:24:26.309374+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.3 | 252.28539.662 | release | `macM1` | `2ece772b248dfe4d810f5655b894e2851d3e1a70d09f3d88bb85cd5c465d8be8` | Retrying | 0/5 | 2026-11-09T01:25:38.659562+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.3 | 252.28539.662 | release | `mac` | `2b3ff70d09bf067405d94b39ca1c62b96f2e734a2e14775b1cb086fe31cdc74d` | Retrying | 0/5 | 2026-11-09T01:25:51.556606+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.2 | 252.26199.634 | release | `macM1` | `e98d1234b2e4bc702ced632261bf03fcf3f2d5fc1ce2840a63204997585bb45a` | Retrying | 0/5 | 2026-11-09T07:41:25.650701+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.2 | 252.26199.634 | release | `mac` | `30aa3fbe579da1bc46e3ce2b7b7e77c94f9935cea0bfbfa88f99ff2a17f22ef9` | Retrying | 0/5 | 2026-11-09T07:41:50.544810+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.1 | 252.26199.587 | release | `macM1` | `d409c82b06cab622dc469d6929e291e40b81b21e1e4b784833d07eb7697f5f61` | Retrying | 0/5 | 2026-11-09T07:51:07.840561+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2.1 | 252.26199.587 | release | `mac` | `e0b2644918ffe76b10001fc7904a58b2ec88cda2d317b10508d3bac784a490b2` | Retrying | 0/5 | 2026-11-09T07:51:32.412186+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-RC1 | 252.23892.426 | eap | `macM1` | `f02855eb67c896e1a8431bc04d1b580884133bbbb0490675f5c4ca5b105dd6ab` | Retrying | 0/5 | 2026-11-09T07:54:19.440615+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-RC1 | 252.23892.426 | eap | `mac` | `24989c23592b9d3c133e9b90d232c4145c392bb48776ce25ab4a71e75f052d21` | Retrying | 0/5 | 2026-11-09T07:54:41.658974+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-EAP2 | 252.23309.308 | eap | `macM1` | `e2b9cdf3e143b976925ecb63ff2aa073c4315819bc5b1dad5068c91ae7c353db` | Retrying | 0/5 | 2026-11-09T07:54:53.472446+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-EAP2 | 252.23309.308 | eap | `mac` | `cf9ce5118250ecf5fce91146675661a9e32ea3091f869ba3aaf8ede35aaec226` | Retrying | 0/5 | 2026-11-09T07:55:07.450087+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-EAP1 | 252.18003.138 | eap | `macM1` | `8e90a0994786e4970d58da45be9ecff72ff1442d25b5a1b98f81cf0fbe01c7da` | Retrying | 0/5 | 2026-11-09T07:55:19.666155+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2-EAP1 | 252.18003.138 | eap | `mac` | `ce745a58d566910f802759601435bb387d4ed1fbd91569d0e26f603c97127a41` | Retrying | 0/5 | 2026-11-09T07:55:41.898657+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2 | 252.23892.529 | release | `macM1` | `5f1822a639b199ec3c2ca7f2352277bfc1727e4e46976bdab71fabf7fe62a280` | Retrying | 0/5 | 2026-11-09T07:53:28.393027+00:00 | application: Invalid application metadata: Invalid file |
| 2025.2 | 252.23892.529 | release | `mac` | `7fd49bfac7e9150e2827d7c6b9f1ad24405963b50efa948492e3ec3202b0ac84` | Retrying | 0/5 | 2026-11-09T07:53:55.416864+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.5 | 251.29188.797 | release | `macM1` | `32b85f6503c3bfb4b88a06f447ee9012b8cbea744f0252e77d08ff5bd75053a2` | Retrying | 0/5 | 2026-11-09T01:22:51.476723+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.5 | 251.29188.797 | release | `mac` | `18194dc7fbd405fe5557e7157094f2beef897fe8c447b9b9caeef2b8939a3b83` | Retrying | 0/5 | 2026-11-09T01:23:04.351467+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.4 | 251.28774.766 | release | `macM1` | `47afa7b7fc6c7a82b5e64f2d1725de29a965aca340d9a149cd1248c7b4b99298` | Retrying | 0/5 | 2026-11-09T01:24:38.340020+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.4 | 251.28774.766 | release | `mac` | `59ad190b3fee784cfedba7f760b48a3db8e9502f78ee6ddd64fc614413b49eb7` | Retrying | 0/5 | 2026-11-09T01:24:49.340189+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.3 | 251.28774.742 | release | `macM1` | `9d914109194d65a509dd5b5db34bc147a6cce9547de2de3e47ea9508b1c7dfb6` | Retrying | 0/5 | 2026-11-09T01:26:04.429990+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.3 | 251.28774.742 | release | `mac` | `ca549bbd2972bf8d1c9cfc29e79b5279ab6d71ab68114ab9c705646c7eaa4511` | Retrying | 0/5 | 2026-11-09T01:26:17.454058+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.2 | 251.28774.648 | release | `macM1` | `baba74abde5bd520938571e00370b07412abfcddc7e358dcf2ea081d0390bfe9` | Retrying | 0/5 | 2026-11-09T07:42:14.445289+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.2 | 251.28774.648 | release | `mac` | `a2054947ca66316172706dfa751e74925f05ece967f8d2496d0c82a96cc3131f` | Retrying | 0/5 | 2026-11-09T07:42:37.528138+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.1 | 251.28774.610 | release | `macM1` | `eb2123398eb1d89c32e95cf884f960d6a4f8ef86669034d1f30a2540f0af2eb0` | Retrying | 0/5 | 2026-11-09T07:51:43.380519+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1.1 | 251.28774.610 | release | `mac` | `879a1ecef2a0f2203ec8739af2f2dd77b7a3d4cc6bf0f0e3070912cded7f57da` | Retrying | 0/5 | 2026-11-09T07:51:55.356027+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1-RC1 | 251.23774.284 | eap | `macM1` | `b7e8e941aabf71c13d96d9b6b720207fe96997057469f1f579b64fa1e119b713` | Retrying | 0/5 | 2026-11-09T07:58:35.426049+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1-RC1 | 251.23774.284 | eap | `mac` | `4c95eb979af53d2b138248b03c0370c94b51601cc9817814dbfe86b65757a318` | Retrying | 0/5 | 2026-11-09T07:58:47.673839+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1-EAP1 | 251.23774.153 | eap | `macM1` | `ad7daecf4f0cb77f76fb78b150f8e7224fc1da841403609739110c3c211e8498` | Retrying | 0/5 | 2026-11-09T07:59:58.255916+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1-EAP1 | 251.23774.153 | eap | `mac` | `b714d662e490753fb1842e6905e38f4083cda48f3fdbaa7b4306579a523f8105` | Retrying | 0/5 | 2026-11-09T08:00:25.477995+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1 | 251.23774.423 | release | `macM1` | `cb2aaa6311252a655ef55f813d3dff78890c2a10cf0aeff885018c316390486b` | Retrying | 0/5 | 2026-11-09T07:57:56.290088+00:00 | application: Invalid application metadata: Invalid file |
| 2025.1 | 251.23774.423 | release | `mac` | `1ddae8569c8a96beeb5e85d20f1eed9115ace532a1154b5624f526cb49ddeaa8` | Retrying | 0/5 | 2026-11-09T07:58:09.502747+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.5 | 243.28141.665 | release | `macM1` | `c8c4b66889a01817116dcef9e46dc934f6bd43c9a9bdac8a667fc9ad6d809a98` | Retrying | 0/5 | 2026-11-09T07:43:02.486388+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.5 | 243.28141.665 | release | `mac` | `f4fab9dd813fd0f80aac713fbc2872c03c2905e1e486e10e64fe1d5c6bc444b2` | Retrying | 0/5 | 2026-11-09T07:43:26.513193+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.4 | 243.28141.657 | release | `macM1` | `81d8601bcd52b613ca193ca0e4d5e93e77f3c682c0e046994013e5e3395c2a69` | Retrying | 0/5 | 2026-11-09T07:52:19.718696+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.4 | 243.28141.657 | release | `mac` | `16237241c9753a318660e5da6ef8e0b6cd8ec57dde763c77fcf6b5b01df843b5` | Retrying | 0/5 | 2026-11-09T07:52:30.357652+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.3 | 243.26053.638 | release | `macM1` | `7f0d70d996f13c9ffda7f11982dc0b323a5a2c7606d893b2f72c0923006126a3` | Retrying | 0/5 | 2026-11-09T07:56:05.441130+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.3 | 243.26053.638 | release | `mac` | `67a6f28d6928da6cd70beaef56267b8423cdc1651645b7fddabb7f04cadf150a` | Retrying | 0/5 | 2026-11-09T07:56:17.853330+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.2 | 243.24978.603 | release | `macM1` | `9e6b8fb53418cef55bdbc690cc1c817f39b12b81cc3985522c24ee7f6fa5c364` | Retrying | 0/5 | 2026-11-09T07:59:12.468267+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.2 | 243.24978.603 | release | `mac` | `09b69187d9feb5e17865fcdec88ce8a95c4933a8176e37a224c251b60d5aed01` | Retrying | 0/5 | 2026-11-09T07:59:25.481523+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.1 | 243.24978.546 | release | `macM1` | `d5000f7309d36ce65929bcdc85b36f543cadb2a5cc2f0675b35edb69489bde8e` | Retrying | 0/5 | 2026-11-09T08:00:37.539687+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3.1 | 243.24978.546 | release | `mac` | `a36d46d6a29f5f86991b1d1e8272bbc27bf00a2c5e562fe7fb3f95075badc85c` | Retrying | 0/5 | 2026-11-09T08:00:50.353723+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3-RC1 | 243.21565.368 | eap | `macM1` | `0dc07e5f146e7735eafc64cfc981ad298dee7cc69b2fdf1015986ea66efb605f` | Retrying | 0/5 | 2026-11-09T08:02:34.357695+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3-RC1 | 243.21565.368 | eap | `mac` | `511bc40cf6eb34a308485c03d0877e8d4f783b9dca93a614f594a892d9e6e863` | Retrying | 0/5 | 2026-11-09T08:03:00.459827+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3-EAP1 | 243.21565.167 | eap | `macM1` | `613e3fa63413319955ff6a6c6e6a1a35987fb219fa9d005b7f250bbdb92d1f72` | Retrying | 0/5 | 2026-11-09T08:03:25.213913+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3-EAP1 | 243.21565.167 | eap | `mac` | `68689277b520c5eeb005dd240766f314fbab4cd1fb35042c75e3e5714576b830` | Retrying | 0/5 | 2026-11-09T08:04:04.546026+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3 | 243.21565.447 | release | `macM1` | `9c7118db757ba4fa7b6725efa5b006f4e6db47ca2b2948a92e43c435329c9c79` | Retrying | 0/5 | 2026-11-09T08:01:42.345987+00:00 | application: Invalid application metadata: Invalid file |
| 2024.3 | 243.21565.447 | release | `mac` | `a5476c8aa604f3c37c192a5301eebf1c33d2ae733be018f485f3bf48d2a52366` | Retrying | 0/5 | 2026-11-09T08:02:08.326516+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.6 | 241.19416.1452 | release | `macM1` | `9050205c1883efefe018e44196c1504b01174ed423e3d9fdbbbd14a23b0e945b` | Retrying | 0/5 | 2026-11-09T07:43:51.433811+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.6 | 241.19416.1452 | release | `mac` | `e4c4d914bda62ebae78f41d97c67ee36a1e0faa99fa2cdafb03788b8af645b9c` | Retrying | 0/5 | 2026-11-09T07:44:13.541881+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.5 | 241.19416.1416 | release | `macM1` | `cfd35be17a315572914586bc9b76100952b1bf2529026240e95001bac0e70dc2` | Retrying | 0/5 | 2026-11-09T07:52:44.291613+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.5 | 241.19416.1416 | release | `mac` | `e780e907650ccc41e062916febfb3ba8bcfa6c2e0ca5166215af89731dbcd4df` | Retrying | 0/5 | 2026-11-09T07:53:06.344927+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.4 | 241.19416.1333 | release | `macM1` | `eac0f635fb8094d1b217780f18d207b661adf76d2477a5f977545bfe7c972341` | Retrying | 0/5 | 2026-11-09T07:56:30.745700+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.4 | 241.19416.1333 | release | `mac` | `a2a1410de2e8a7ded192855d343d4c1b77f8bc9b4c43e9f056cde13249a7c0cf` | Retrying | 0/5 | 2026-11-09T07:56:42.493056+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.3 | 241.19072.1291 | release | `macM1` | `80947e27810c0c00618f95bfc6a96d1cf68100e6f9b43fe67b7987a389752b44` | Retrying | 0/5 | 2026-11-09T07:59:37.352059+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.3 | 241.19072.1291 | release | `mac` | `011a816126cdab989d2eff5edc35486a1a097d646ea32c1d4a16d4591879f933` | Retrying | 0/5 | 2026-11-09T07:59:47.360152+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.2 | 241.19072.1238 | release | `macM1` | `0b38553a91697d1f8c9570074c9db6d0271b2456124c1cdd860d2a1502cbfdff` | Retrying | 0/5 | 2026-11-09T08:01:02.408773+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.2 | 241.19072.1238 | release | `mac` | `59470cae0d7307cb7d7c37d8b39449a3d0f64bb443a3f7bd0d75ab8f1aba35ad` | Retrying | 0/5 | 2026-11-09T08:01:14.408980+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.1 | 241.19072.1155 | release | `macM1` | `381b6c527f444ca2ea652054e172afee2096c29ad445cec7fa7fe6432cb41bea` | Retrying | 0/5 | 2026-11-09T08:04:29.877705+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1.1 | 241.19072.1155 | release | `mac` | `85f936a8d4a610b0232f5716f364cfae6edac5322fd40714c07e9ffabb11e85a` | Retrying | 0/5 | 2026-11-09T08:04:53.469419+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-RC1 | 241.18034.990 | eap | `macM1` | `4767d9b85ac5842fcb850ddb143e0871ae6986f03dec5f019fe55cd88d8349e2` | Retrying | 0/5 | 2026-11-09T08:09:31.480690+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-RC1 | 241.18034.990 | eap | `mac` | `f7e1bc1c66430cc709a3d71d712604354f84c02c77eeec78eb7cda13b5b6857c` | Retrying | 0/5 | 2026-11-09T08:09:54.557514+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-EAP2 | 241.17011.787 | eap | `macM1` | `95649b078db3e289f9c25bba90a0d6d7ffc9ef753699f0108870b3afa07e9509` | Retrying | 0/5 | 2026-11-09T08:10:16.519965+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-EAP2 | 241.17011.787 | eap | `mac` | `ba2aeab16fbf38924af3cdddc41579ddf9c49e2e6c31ef03ff2a97f9cce499b4` | Retrying | 0/5 | 2026-11-09T08:10:38.619568+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-EAP1 | 241.17011.705 | eap | `macM1` | `09d5a6baaefbf7c952acc4a578ff8c95e28ac50970dbf05f3647a837dd4cdcfa` | Retrying | 0/5 | 2026-11-09T08:12:30.590073+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1-EAP1 | 241.17011.705 | eap | `mac` | `42b230874364a27b9c47940e1c773107c24b2beaf48c9babe42d29ece7bac804` | Retrying | 0/5 | 2026-11-09T08:12:53.521223+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1 | 241.18034.1093 | release | `macM1` | `2b070b9eb87fc910ef8b2ff96479e724f64864b6825375c272e1f7c604bbc4e7` | Retrying | 0/5 | 2026-11-09T08:08:03.784039+00:00 | application: Invalid application metadata: Invalid file |
| 2024.1 | 241.18034.1093 | release | `mac` | `93510db63ab6f3d7b6e139730f90836ba772032526d77e3de207e848c808d398` | Retrying | 0/5 | 2026-11-09T08:08:27.608328+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.3 | 233.15619.1160 | release | `macM1` | `3435a36bcc5c57d27d05d073892f19230db03e18863cdbcccd56435f184427fe` | Retrying | 0/5 | 2026-11-09T07:57:02.368702+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.3 | 233.15619.1160 | release | `mac` | `3836f0fbced07da9990297a90a9c958390c450dd91795bbc01dcec1a56183756` | Retrying | 0/5 | 2026-11-09T07:57:23.427695+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.2 | 233.15619.1151 | release | `macM1` | `6bbc0c00b85b6cdeb53cd4c9e4b2d6fa81f9180d30f16b74dd94690095feb327` | Retrying | 0/5 | 2026-11-09T08:05:15.937803+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.2 | 233.15619.1151 | release | `mac` | `579d93078a1dde38c41513889a06fb5bbda7d6437da6bfcb8fe907ea45c9fc6d` | Retrying | 0/5 | 2026-11-09T08:05:36.412255+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.1 | 233.13135.1068 | release | `macM1` | `d7512decb18b8df940f7e5d7a8f15c85e3c2ad236202f5d7369cdc24dacf480f` | Retrying | 0/5 | 2026-11-09T08:11:02.426770+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3.1 | 233.13135.1068 | release | `mac` | `8dfc7754f4fd20d07630ef86b1ff985e96c5e0183b7a4624b7d2de5139a6ac2c` | Retrying | 0/5 | 2026-11-09T08:11:23.701487+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3-RC1 | 233.13135.841 | eap | `macM1` | `0e40a76e6dcd644ab0cb0c5a7d50c768a79a96e8e5adbc61c5da3127455e2d9b` | Retrying | 0/5 | 2026-11-09T08:14:43.381013+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3-RC1 | 233.13135.841 | eap | `mac` | `84eee26dfbc298c8ee72e5d30871b2ea4f62a58a50439d1e248b4df288404edb` | Retrying | 0/5 | 2026-11-09T07:47:30.429303+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3-EAP1 | 233.11799.543 | eap | `macM1` | `8a83047d033f31760d980a4b1546a9b28e8b4b2c5c1d45e3e490bf7e9250f7ab` | Retrying | 0/5 | 2026-11-09T07:47:53.380386+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3-EAP1 | 233.11799.543 | eap | `mac` | `d69f9671aa8987a693c34b3e1d84289d749fc0ec7666b9d0e492f759e19b45a8` | Retrying | 0/5 | 2026-11-09T07:48:14.428956+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3 | 233.13135.979 | release | `macM1` | `133e5bae81d675a6ee7780efec18dd96dfed059dbfdd2ad4a1028d9956a1ec6e` | Retrying | 0/5 | 2026-11-09T08:13:57.573201+00:00 | application: Invalid application metadata: Invalid file |
| 2023.3 | 233.13135.979 | release | `mac` | `c1e46dcb3429772b164f423cedc644f388217d1e7310d682b2341f9e744333bf` | Retrying | 0/5 | 2026-11-09T08:14:19.590172+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.3 | 232.10335.1075 | release | `macM1` | `199bc31d5e10f9cb7c638cfe618cd64824ed35aa320d3797d5dbf2ce54bea145` | Retrying | 0/5 | 2026-11-09T07:57:33.262307+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.3 | 232.10335.1075 | release | `mac` | `5364ae0c18eea3c1886ba2b2574c4a6db1270b8dab3dc85c6217f2136989c6b1` | Retrying | 0/5 | 2026-11-09T07:57:45.398156+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.2 | 232.10335.1039 | release | `macM1` | `5320d0eedb8c1c390521444baaf2bf47b5053c00f09e1384396c047ad0646821` | Retrying | 0/5 | 2026-11-09T08:05:58.634952+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.2 | 232.10335.1039 | release | `mac` | `7e9cab1681ae815a333d817090d9171af91e988c2f75f9f88960b6eb43a88bef` | Retrying | 0/5 | 2026-11-09T08:06:19.381599+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.1 | 232.10300.938 | release | `macM1` | `2a4bf80db03d0c1dd64d83ea3678d47a232b6b040f5dd8b80dac98c07bb7982f` | Retrying | 0/5 | 2026-11-09T08:11:44.008591+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2.1 | 232.10300.938 | release | `mac` | `6e8cb6bbabd75b037d8230a5cb1bfaff0be4e76029950e06cd62165bfc04864f` | Retrying | 0/5 | 2026-11-09T08:12:07.528250+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2-RC1 | 232.8660.663 | eap | `macM1` | `5103336676685b9eeaa9420a33452c133e6262f893b38e3bc9c92b5cd001222d` | Retrying | 0/5 | 2026-11-09T08:16:08.399952+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2-RC1 | 232.8660.663 | eap | `mac` | `907a08ce3cbe0f1133ce013c25bfa1202e0c980c602e06953158ee10ca40dadc` | Retrying | 0/5 | 2026-11-09T08:16:32.736266+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2-EAP1 | 232.8660.471 | eap | `macM1` | `95c9413ace3b28eea02dbcb2a3691adb465490ca7d965aa45df384921bbd0958` | Retrying | 0/5 | 2026-11-09T08:16:59.066712+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2-EAP1 | 232.8660.471 | eap | `mac` | `861d46655f8d734ce6f4d67e718efcb72e8ecc13166abf30df920035c0a088cb` | Retrying | 0/5 | 2026-11-09T08:17:21.518867+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2 | 232.10072.781 | release | `macM1` | `a19ecd8a109783e9d2260cc18f48ac97e52a0bc00ee29df5ccf711a80d1701eb` | Retrying | 0/5 | 2026-11-09T07:50:35.343679+00:00 | application: Invalid application metadata: Invalid file |
| 2023.2 | 232.10072.781 | release | `mac` | `11a635432beaca5809fe0253303d07444a0bfd6fac287c72e7b03e7a9f1a59e4` | Retrying | 0/5 | 2026-11-09T08:15:05.417816+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.3 | 223.8836.1611 | release | `macM1` | `901ebad11a728f0b449233494d530a1c1a4c3e51d90b1328cbb58c28a76e50aa` | Retrying | 0/5 | 2026-11-09T08:06:40.522495+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.3 | 223.8836.1611 | release | `mac` | `8a59c4024d5cb6469703b138c169c726ad9ed5ca390160620287b5debf96da3f` | Retrying | 0/5 | 2026-11-09T08:07:01.456849+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.2 | 223.8836.1550 | release | `macM1` | `ca30f94247eec12470055a789228bd594393a9c944a9dffc18db291ee9e074cb` | Retrying | 0/5 | 2026-11-09T08:08:50.446291+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.2 | 223.8836.1550 | release | `mac` | `4e1f2d26ce716559b7a8f96d33dcbb678732a8c3c3210500cd83eaa53fd03dd3` | Retrying | 0/5 | 2026-11-09T08:09:10.415146+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.1 | 223.8836.1366 | release | `macM1` | `39dd6e9bc93cee7f4dfbebd44620a981ed4157778dfc0461c88cb51a65d83798` | Retrying | 0/5 | 2026-11-09T07:49:51.574811+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3.1 | 223.8836.1366 | release | `mac` | `87ab59549a73e943fb7386a3ac7755852cd663599303c5d1e7b8c1aa2398cb44` | Retrying | 0/5 | 2026-11-09T07:50:13.419305+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3-RC1 | 223.8836.1121 | eap | `macM1` | `7e6914eef73a37e03e3478548c308abc554eb522d2c431ff7d88cc16098ff79a` | Retrying | 0/5 | 2026-11-09T08:19:55.586818+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3-RC1 | 223.8836.1121 | eap | `mac` | `0a152eaad86cb37e906345417c4683d92361978e83dd89fa31beea313350d369` | Retrying | 0/5 | 2026-11-09T08:20:16.343556+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3-EAP1 | 223.7571.953 | eap | `macM1` | `8c825e2a23b713a3e3299371750bf35ce4959984e7571158fd961c9a3638ac0a` | Retrying | 0/5 | 2026-11-09T08:20:37.360466+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3-EAP1 | 223.7571.953 | eap | `mac` | `af816bf5713f844742d429017311520e9f0bdf9babbcf1f72da78dcf0efa87e7` | Retrying | 0/5 | 2026-11-09T08:21:00.446831+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3 | 223.8836.1185 | release | `macM1` | `40d8a928a1c1703544c9905a3f8e6a7d0ade3b17302782da2ed68fd1dcdafef9` | Retrying | 0/5 | 2026-11-09T08:19:14.235364+00:00 | application: Invalid application metadata: Invalid file |
| 2022.3 | 223.8836.1185 | release | `mac` | `17cb973af11118c246d4144ba0071ce31fe3f276be7029f613cdb0fa60b752cc` | Retrying | 0/5 | 2026-11-09T08:19:35.395600+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.4 | 222.4554.1739 | release | `macM1` | `7718362c21279623acd921547bc4b2d10a6f0418f9bdb6eb334a85740d7038a3` | Retrying | 0/5 | 2026-11-09T08:07:21.458935+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.4 | 222.4554.1739 | release | `mac` | `d078ad25eddf8e27b5ff1727e3c9c500a29ff180b9e0b947bef243e8ec5f4724` | Retrying | 0/5 | 2026-11-09T08:07:43.350566+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.3 | 222.4554.1662 | release | `macM1` | `50821eb8da7065a5f6a7905314ee616ea0b1512038b5e307c7ed1e7d252d6a69` | Retrying | 0/5 | 2026-11-09T08:13:14.669253+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.3 | 222.4554.1662 | release | `mac` | `6e39c8231fedaab80adc62f6ec8fcba2b3a7516c564c69246ad248a54f0ce797` | Retrying | 0/5 | 2026-11-09T08:13:35.530954+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.2 | 222.4554.1547 | release | `macM1` | `29e65eebe94908eb27adfa307e5d7ff4a15936caf351a13826ec6c3596c1131e` | Retrying | 0/5 | 2026-11-09T07:48:35.514607+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.2 | 222.4554.1547 | release | `mac` | `507eae1670942527fb12c6712e3deaf301075a9d2811e71a36567967377646a1` | Retrying | 0/5 | 2026-11-09T07:48:54.344134+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.1 | 222.4554.1426 | release | `macM1` | `c88fa5676c993f9f0d9efd467830248d61a4c2204ab5061e88501a401d8e71c9` | Retrying | 0/5 | 2026-11-09T08:18:24.403825+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2.1 | 222.4554.1426 | release | `mac` | `9345e7832e7197bb7311ecc089d657148601df1e3587192eadb61dadec0e8285` | Retrying | 0/5 | 2026-11-09T08:18:50.671605+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2-RC1 | 222.3345.1195 | eap | `macM1` | `20fe6ea39c8ac7f8510c25bd0ae1bfe4758b09a9937eaa1d798f1eb8fa887fa1` | Retrying | 0/5 | 2026-11-09T08:22:48.487790+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2-RC1 | 222.3345.1195 | eap | `mac` | `142bcbc8d80c23796ff4faa594ff599fa9a26b20d412ed428feb39e75dd5cb37` | Retrying | 0/5 | 2026-11-09T08:23:12.528400+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2-EAP1 | 222.3345.848 | eap | `macM1` | `5556b01b17d73f093f54f3db0bfca0a0b5abec59617ed99c1b753281403d6fd3` | Retrying | 0/5 | 2026-11-09T08:24:11.774096+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2-EAP1 | 222.3345.848 | eap | `mac` | `29cd5bcc202e06f2015f07bfbaa097ec644ca2f71982fd77c3d534c9cc41635c` | Retrying | 0/5 | 2026-11-09T08:24:33.741974+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2 | 222.3345.1295 | release | `macM1` | `bdc83d9c7a3430cc2b0b0361a9e4eab82e951bfe87f0e4754106d09850947077` | Retrying | 0/5 | 2026-11-09T08:22:05.880390+00:00 | application: Invalid application metadata: Invalid file |
| 2022.2 | 222.3345.1295 | release | `mac` | `4e36c60d281596c220287ab2191165be37ef01c3c54ab5f5e4e535c8b81bc754` | Retrying | 0/5 | 2026-11-09T08:22:27.565224+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.5 | 213.7172.1189 | release | `macM1` | `89e50de2d912b03fb6d49581acdf12fa8699447e2dd1c81cfc0897a1edbe56b5` | Retrying | 0/5 | 2026-11-09T07:49:15.297160+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.5 | 213.7172.1189 | release | `mac` | `79b1e587589f0144c6a7e479c6c40c8dbfe6d364ef7c8d3b9a8c9403243c376f` | Retrying | 0/5 | 2026-11-09T07:49:33.432967+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.4 | 213.7172.1146 | release | `macM1` | `295a979abd974664360ee73f2650291a33ca2eb5afc59d2e6cb0a082c7aeceea` | Retrying | 0/5 | 2026-11-09T08:15:28.424798+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.4 | 213.7172.1146 | release | `mac` | `5a5805471ab19589c071c435495294fb5ee86abb5a2e7347e4f72f0bbf27df4b` | Retrying | 0/5 | 2026-11-09T08:15:47.737173+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.3 | 213.7172.1079 | release | `macM1` | `0432578184d1c013b8f1f840a8fa48e8e6284731b7e31b5759842f42967eb7eb` | Retrying | 0/5 | 2026-11-09T08:17:44.544807+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.3 | 213.7172.1079 | release | `mac` | `6137d77d33a8b83c0048c098246f3b4666fe35faffdb5724e945d5e7a085b35e` | Retrying | 0/5 | 2026-11-09T08:18:04.368719+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.2 | 213.7172.1022 | release | `macM1` | `00b8655186d5a5f56b98788e48f918c7713c855260eb17b4939e691f0aff9c58` | Retrying | 0/5 | 2026-11-09T08:21:28.402946+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.2 | 213.7172.1022 | release | `mac` | `599b2dc30b0de3e00c17b0e111e7af63a5648a72aa22aec4b4e47d4e0dc1aaf4` | Retrying | 0/5 | 2026-11-09T08:21:47.389959+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.1 | 213.7172.958 | release | `macM1` | `3104eb7b2a363ef9602b86a8fdca02d9b55264127f481f3eabbed65979b34791` | Retrying | 0/5 | 2026-11-09T08:24:57.910751+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3.1 | 213.7172.958 | release | `mac` | `06f06e121a552a7c4ee89ecbdecb4ac7d1978ae87d6c80d04837a19e92e4f90d` | Retrying | 0/5 | 2026-11-09T08:25:17.624360+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-RC1 | 213.6461.785 | eap | `macM1` | `845e024312fa5f505df06a6350c28762c9bd64abb988dc45ea5b623909afabd0` | Retrying | 0/5 | 2026-11-09T08:28:09.452434+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-RC1 | 213.6461.785 | eap | `mac` | `ead66bda64c2fe7cc2a7f8f1d48bbce2df9e4b81ba609cd1da3b5c3182ddc14b` | Retrying | 0/5 | 2026-11-09T08:28:19.360534+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-EAP2 | 213.5744.663 | eap | `macM1` | `50d345ae555eec884d398cfeea96ab3c6638ec5797c857f224e7254b4b6cf59f` | Retrying | 0/5 | 2026-11-09T08:28:29.867122+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-EAP2 | 213.5744.663 | eap | `mac` | `f449e6dd87e6118fad9df69801a62497817afadf268defdcf47c44476784111d` | Retrying | 0/5 | 2026-11-09T08:28:38.290293+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-EAP1 | 213.5744.587 | eap | `macM1` | `1893efc242dd441c2e6f8c57ec2911dfb7e1fc1e25aea7327a5f3b54aba96e22` | Retrying | 0/5 | 2026-11-09T08:28:49.497964+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3-EAP1 | 213.5744.587 | eap | `mac` | `a931be388ba3c72bd39389dd129962840e789f60b916d493bee3e1c1392352a1` | Retrying | 0/5 | 2026-11-09T08:29:00.668573+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3 | 213.6777.846 | release | `macM1` | `3ace6d45db718dffd80bf126a76735fb65099de292112a01cc078aa61c475a70` | Retrying | 0/5 | 2026-11-09T08:27:32.533299+00:00 | application: Invalid application metadata: Invalid file |
| 2021.3 | 213.6777.846 | release | `mac` | `2c5517518fec31ac960e4309fa848ad831f9048ef15df1b362e12aa8f41d9dbd` | Retrying | 0/5 | 2026-11-09T08:27:50.593836+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.6 | 212.5284.1433 | release | `macM1` | `9f9a8b3f640a8bff2efb1bd8727534bc2d58351977c3fa6363ec8f30f8d33fea` | Retrying | 0/5 | 2026-11-09T08:23:33.606760+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.6 | 212.5284.1433 | release | `mac` | `f3d08c6306a1d806308f8949b126befa75cbe93d86cc907f466d72b2b994c8d0` | Retrying | 0/5 | 2026-11-09T08:23:53.533024+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.5 | 212.5284.1355 | release | `macM1` | `31861c7e244c1ebc3c998f345e6dc6ce28d249235cefa9e4ae7db91d229e57d0` | Retrying | 0/5 | 2026-11-09T08:25:37.691689+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.5 | 212.5284.1355 | release | `mac` | `96b6077db41307fadaf8cb0a6d4e1cabaf157b6ca6cc4fa5a7a89cee3704262e` | Retrying | 0/5 | 2026-11-09T08:25:56.544176+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.4 | 212.5284.1340 | release | `macM1` | `df22a8a7146e81375af3d18e314eb81d10891c9a57fbd66e5ff61374c978a7fe` | Retrying | 0/5 | 2026-11-09T08:26:54.476032+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.4 | 212.5284.1340 | release | `mac` | `6353efb5541fa4771705577817eba377c67edd2091b996e3485d14864e9ce9f3` | Retrying | 0/5 | 2026-11-09T08:27:14.440223+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.3 | 212.5284.1281 | release | `macM1` | `86d6ab1d727c612dca694396caf26732a0fbdc016f0e4a6f88df642ba2e88a90` | Retrying | 0/5 | 2026-11-09T08:29:27.404217+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.3 | 212.5284.1281 | release | `mac` | `006e3eca78d9b7a4d3148e727731b70f06a9e1a2528e2bbe6c297ca3011a6ae7` | Retrying | 0/5 | 2026-11-09T08:29:36.262887+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.2 | 212.5284.1234 | release | `macM1` | `e0060854417b86e62362bf53d2b72efae6abcedf4a5dc18ad65b442ce6ffb51b` | Retrying | 0/5 | 2026-11-09T08:29:56.612603+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.2 | 212.5284.1234 | release | `mac` | `11e80c58039c5e3ea4c49a7aecd697494d12c84d5704a80d9ae1456d4cf8eda2` | Retrying | 0/5 | 2026-11-09T08:30:13.430595+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.1 | 212.5284.1175 | release | `macM1` | `f393a5cf68ae79b229cbbcb640a7fd64fb10cd5958ad45a04af3fa4fc4d10427` | Retrying | 0/5 | 2026-11-09T08:30:31.500539+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2.1 | 212.5284.1175 | release | `mac` | `c2387d84c974582ac959e90d17baef331254f1dbda41579fb333228ab9e9d6dd` | Retrying | 0/5 | 2026-11-09T08:30:50.444314+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-RC1 | 212.4746.1036 | eap | `macM1` | `04412c93a4b48f08d4e1acd86365c0252dbf382191c7e91a72a9b7a1f71d3639` | Retrying | 0/5 | 2026-11-09T08:31:48.287480+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-RC1 | 212.4746.1036 | eap | `mac` | `67554c8c95ebb6fbfe25739419210c92d81f4d5476411c6a43762d576d7ab8e3` | Retrying | 0/5 | 2026-11-09T08:32:05.674303+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-EAP2 | 212.4746.950 | eap | `macM1` | `9b514d1032eb8ae103aedbccb305d0d4e2ad519fbc869fafb1462e55951d3587` | Retrying | 0/5 | 2026-11-09T08:32:23.467316+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-EAP2 | 212.4746.950 | eap | `mac` | `c86abf2711c1bd62d41876aad56496fdd5b166745c47eb01d129bd36ad948e52` | Retrying | 0/5 | 2026-11-09T08:32:41.547994+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-EAP1 | 212.4416.671 | eap | `macM1` | `8b32eadcb115a785019406e5611553bd78e682082db924ef13697a8d18c0856b` | Retrying | 0/5 | 2026-11-09T08:34:06.442502+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2-EAP1 | 212.4416.671 | eap | `mac` | `b14a69d4286e825bebe47449d33ce07893a920671fdb5d4b629446d14569b819` | Retrying | 0/5 | 2026-11-09T08:34:24.378084+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2 | 212.4746.1141 | release | `macM1` | `eab743e73c8d7dbe34b02980f3b3c1756c362896729f227f0bb5fb077e18ee09` | Retrying | 0/5 | 2026-11-09T08:31:10.287559+00:00 | application: Invalid application metadata: Invalid file |
| 2021.2 | 212.4746.1141 | release | `mac` | `4ee2310961eb7cb6acdad408f39f74b24cf7131fc6be9e6d5c05b9aa3f1703d4` | Retrying | 0/5 | 2026-11-09T08:31:29.573009+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.4 | 211.7628.1509 | release | `macM1` | `5ffbfe638e6bcc9dcbf4450471d690c5faa3c231e11eaae9bbf350870042ab5f` | Retrying | 0/5 | 2026-11-09T08:26:16.393825+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.4 | 211.7628.1509 | release | `mac` | `e54041cddce2d80e0426e8bb35327133c2d1db3748f0702878a55ebf684ea64b` | Retrying | 0/5 | 2026-11-09T08:26:36.709771+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.3 | 211.7628.1405 | release | `macM1` | `2a8b71040a093229e14f171ee9a9f7bf181a156841bb8beca584b2a8896490a5` | Retrying | 0/5 | 2026-11-09T08:32:59.805779+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.3 | 211.7628.1405 | release | `mac` | `bef5c7d35f4bc8b0ce08edf3ccf76ef3ab8e0cda05f26fda970085e844b5842f` | Retrying | 0/5 | 2026-11-09T08:33:16.381560+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.2 | 211.7628.1389 | release | `macM1` | `998d50c719242407deec3923b7a49e1b26c3a8be68629527a155857d6261be77` | Retrying | 0/5 | 2026-11-09T08:33:32.195444+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.2 | 211.7628.1389 | release | `mac` | `9cc2cbf21441765319adc2aabe27202085b3b6a84c2d8503efa6c72bf03eef1b` | Retrying | 0/5 | 2026-11-09T08:33:49.488417+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.1 | 211.7442.1291 | release | `macM1` | `b15c68cf43d89554f8f8272310a4ef0032479d2ec69863153c7603056456e258` | Retrying | 0/5 | 2026-11-09T08:35:15.332758+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1.1 | 211.7442.1291 | release | `mac` | `286451f1691f4e94313ab04b4e37dc106b2c119efc9cd4cf50aa8cbe56540b72` | Retrying | 0/5 | 2026-11-09T08:35:32.620884+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-RC1 | 211.7142.1161 | eap | `macM1` | `b7fd42c178a2bb1a7ad8eb82787c6d65ada84fe93390a166dbb341f35faa15fb` | Retrying | 0/5 | 2026-11-09T08:37:01.434166+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-RC1 | 211.7142.1161 | eap | `mac` | `1196b7d36e395e76b0e6c6075c006106528447aae89e542983de538a0a34a10e` | Retrying | 0/5 | 2026-11-09T08:37:18.408639+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP5 | 211.6693.973 | eap | `macM1` | `0c45ba92325f7407d76fc88c95c029627a44f768950f6a01446df1c1710af933` | Retrying | 0/5 | 2026-11-09T08:37:34.339808+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP5 | 211.6693.973 | eap | `mac` | `0cde340c56801ff4ab12e9056f9ffeb2c79a0e65ce8f508c734d84bb8d6553bd` | Retrying | 0/5 | 2026-11-09T08:37:50.617637+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP4 | 211.6556.833 | eap | `macM1` | `074fa8df197c9d88a58fe8b62df094e1001085712a59a0a8f82e022e732feb20` | Retrying | 0/5 | 2026-11-09T08:38:07.502938+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP4 | 211.6556.833 | eap | `mac` | `9c3d90b509722ceba187064ce2c5d2f822e56f22f7638730e1ea7e60f6e5965e` | Retrying | 0/5 | 2026-11-09T08:38:27.355350+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP3 | 211.6556.759 | eap | `macM1` | `7ad26402cfd0cdaa4ea85378b2add96305ecc570e7b850780e674a233e7fcf3a` | Retrying | 0/5 | 2026-11-09T08:38:44.316912+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP3 | 211.6556.759 | eap | `mac` | `372af3c489bce8d97dd910a1f17ffa39af4814247160fc9705a1268dc52763af` | Retrying | 0/5 | 2026-11-09T08:39:00.444030+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP2 | 211.6085.475 | eap | `mac` | `fbd3527ea3d8a885f6164a1ad5982016aa2242d97a2146c46247e4b0b50a11ae` | Retrying | 0/5 | 2026-11-09T08:40:19.417417+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1-EAP1 | 211.4961.341 | eap | `mac` | `1e28b2227191a48aa88eb0bde15992b2127f6cdd89a6b7e457d9f4754668eaaa` | Retrying | 0/5 | 2026-11-09T08:40:34.358690+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1 | 211.7142.1222 | release | `macM1` | `f8b120ac2e240f59857b888582a2cb59a7d7026210db68b0567434b248403283` | Retrying | 0/5 | 2026-11-09T08:36:25.906829+00:00 | application: Invalid application metadata: Invalid file |
| 2021.1 | 211.7142.1222 | release | `mac` | `3bf2b747cbaea592a9fee7b099df4243016071bc1af911b8e62e991d9e5bd129` | Retrying | 0/5 | 2026-11-09T08:36:42.400520+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.6 | 203.8084.3437 | release | `macM1` | `aa17253f9b29c845f0aad6847294d4832cd73df8474321592fc1854db4763ebf` | Retrying | 0/5 | 2026-11-09T08:29:10.520471+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.6 | 203.8084.3437 | release | `mac` | `bc2bb0c24bfe799e1fad564b8f82519b3504f4875af76eff10d1a39318b2b0af` | Retrying | 0/5 | 2026-11-09T08:29:18.247369+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.5 | 203.8084.3348 | release | `macM1` | `f5a826ab392178ca59808acd7c8a3579debacc63688d908a5dc93626d5c71ae9` | Retrying | 0/5 | 2026-11-09T08:34:43.578708+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.5 | 203.8084.3348 | release | `mac` | `9c1b6ebaffbfe6aecbdd5371af88a8a3220ff92ff7cf15414a03e065914a4f3a` | Retrying | 0/5 | 2026-11-09T08:34:59.093590+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.4 | 203.8084.1447 | release | `macM1` | `afd0fa8f9fc0fb51f2c64a4c18344734596c15648e373049f6898994bdfc18fe` | Retrying | 0/5 | 2026-11-09T08:35:50.508332+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.4 | 203.8084.1447 | release | `mac` | `1e057489d67834ea553124d26eca48bf9c0b8c2c548feb3d0d14464f7dfc27b1` | Retrying | 0/5 | 2026-11-09T08:36:08.518799+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.3 | 203.7717.1351 | release | `macM1` | `101761cfe5dddeea6a25f5f4b0acfdcce398489bdcb56d9ab3b864b69b12208e` | Retrying | 0/5 | 2026-11-09T08:39:19.311062+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.3 | 203.7717.1351 | release | `mac` | `33e7c996d9a37eb48d9c13328a46cf5f4b209a44829ac77ec54c553f78c5a0d3` | Retrying | 0/5 | 2026-11-09T08:39:37.152978+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.2 | 203.7177.1329 | release | `macM1` | `0cab7dfbe3f01ba5d48bfd1073c959c1d63682674a8a51ed81a3325dac8b64cb` | Retrying | 0/5 | 2026-11-09T08:39:53.129959+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.2 | 203.7177.1329 | release | `mac` | `72325f5041f73a4bde7feb73193e12e2923cc8c32a5c337957426713343161aa` | Retrying | 0/5 | 2026-11-09T08:40:02.308713+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.1 | 203.7148.1199 | release | `macM1` | `302168a3aae2ca6d53a2a8b6580f0d3959af8ccb89cdc07b045eb3032943cf9d` | Retrying | 0/5 | 2026-11-09T08:40:50.411662+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3.1 | 203.7148.1199 | release | `mac` | `7ec8d6ff6b6dd4663a852a4cecd9d9dcddf5667974b494cbb5c3d9b501ce8110` | Retrying | 0/5 | 2026-11-09T08:41:08.341874+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3-RC1 | 203.5981.933 | eap | `mac` | `323015a39e797ce24068afd0d22d7cf26b90144256c710a67bf8f984576d6d83` | Retrying | 0/5 | 2026-11-09T08:41:43.234890+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3-EAP4 | 203.5981.851 | eap | `mac` | `e1429dd80105e62dbb6595baafc36d288373d9db0142bd2aa8ddf735e9aa283e` | Retrying | 0/5 | 2026-11-09T08:42:02.803388+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3-EAP3 | 203.5784.751 | eap | `mac` | `1757c161bc8dfccbc599a04643b274532b004ec2252c2d497c2be52a4982ff0b` | Retrying | 0/5 | 2026-11-09T08:42:35.482493+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3-EAP2 | 203.4818.546 | eap | `mac` | `f15b369b9d2b63e6850b873ac03636372c1506cd006eb39be392d2b1defb40e4` | Retrying | 0/5 | 2026-11-09T08:43:15.454313+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3-EAP1 | 203.4818.451 | eap | `mac` | `2a0ed3720b868b45f5bda61837d73ce87a9f87392ff0df2740f741e23cc59098` | Retrying | 0/5 | 2026-11-09T15:59:44.297810+00:00 | application: Invalid application metadata: Invalid file |
| 2020.3 | 203.5981.1014 | release | `mac` | `6973e0d3aab3ab2099d9512bd2a77d6e96692385f27d5d4f49b95fcfa4de279a` | Retrying | 0/5 | 2026-11-09T08:41:24.317636+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2.3 | 202.8194.1069 | release | `mac` | `43e72604518da881c8233c3ae89be4ce71a50169bdfd0b6a01ea4375bf8583be` | Retrying | 0/5 | 2026-11-09T08:42:14.548301+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2.2 | 202.7660.1015 | release | `mac` | `3a4327c976b3c5a058fe857dde4e03b0c58b4a854ea55d063dfdf2fe8199f7bc` | Retrying | 0/5 | 2026-11-09T08:43:35.444482+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2.1 | 202.7319.997 | release | `mac` | `9a8e2cb47f2a9414820f30c7d38c405688e8efcaef0c5c6f6b2cbd409544fdf2` | Retrying | 0/5 | 2026-11-09T08:44:05.382983+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2-RC1 | 202.6397.898 | eap | `mac` | `12bb245cd6d42172885e00fc406cf8c7cd92846415cec20c7abaed62faa36250` | Retrying | 0/5 | 2026-11-09T16:00:05.253739+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2-EAP4 | 202.6397.798 | eap | `mac` | `96cb230cdb74447461f45e84ca7aa337048626039e0eff99d6af05fa6f28deb0` | Retrying | 0/5 | 2026-11-09T16:00:45.284845+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2-EAP3 | 202.6397.665 | eap | `mac` | `119bcc47d41fd09b3d43f00d675453a3cce7b4d3de95d900255c390e09e1a0e6` | Retrying | 0/5 | 2026-11-09T16:01:44.323159+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2-EAP2 | 202.4357.467 | eap | `mac` | `a1ff571713c9d7f666551886ffb3c963d36c1bcf2479a0c368c2d3833a2e5079` | Retrying | 0/5 | 2026-11-09T16:59:24.259385+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2-EAP1 | 202.4357.394 | eap | `mac` | `0f0aa9d5f9c65a5cba07013b6bd19a3d3e7ca8bf4ade428dc1a5c2a8f66ebb8f` | Retrying | 0/5 | 2026-11-09T16:59:48.317021+00:00 | application: Invalid application metadata: Invalid file |
| 2020.2 | 202.6397.948 | release | `mac` | `d105e8cbe05145726e36893fafe2a42867c89bbfe85452486baeb94f1d213ffe` | Retrying | 0/5 | 2026-11-09T15:59:22.402487+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.7 | 201.8743.1619 | release | `mac` | `9c437387349601c0422907ccc4e43766ecc532fc1914c36de00afe55c823bd8e` | Retrying | 0/5 | 2026-11-09T08:42:54.568243+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.6 | 201.8743.1572 | release | `mac` | `55044360483f6ccbad659718e905026c32d8734135a6961e1e5608085b3b8cf7` | Retrying | 0/5 | 2026-11-09T08:43:54.552993+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.5 | 201.8743.1556 | release | `mac` | `b7869e079d7058e06d11f3500196a78c2fb38dd246dbe92698929b1ef9aff033` | Retrying | 0/5 | 2026-11-09T08:44:17.488124+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.4 | 201.8743.1536 | release | `mac` | `76fa44e56d652ce55d017adc9a3ab1d6cf709a77759dcc52daa5f4126b801daa` | Retrying | 0/5 | 2026-11-09T16:00:24.277411+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.3 | 201.8538.1503 | release | `mac` | `03ab31cf173456be36b55dfd2255ccbe2810f7452db82e88ac3f6a158eb2dc29` | Retrying | 0/5 | 2026-11-09T16:02:04.281396+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.2 | 201.7846.1470 | release | `mac` | `2e9cd8bf4e343834dc54027c9bad83ae96f2f510dd8dd2777e82c8437904c702` | Retrying | 0/5 | 2026-11-09T16:59:39.833255+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1.1 | 201.7223.1434 | release | `mac` | `ca7033330a990ecb6d270dd1a693db3b6578a8f9aeb58fe34487599092663c50` | Retrying | 0/5 | 2026-11-09T16:59:56.385830+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.6668.1353 | release | `mac` | `5733fb6efb56f2c4e6c7d08a24f8e76a3fee6e78f48910a8b212467bf279a407` | Retrying | 0/5 | 2026-11-09T17:00:08.245523+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.6668.1274 | eap | `mac` | `54948cf47cc09a41aca57c81f465a167ffdd23903b056685fa262df547be7427` | Retrying | 0/5 | 2026-11-09T17:00:17.228879+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.6251.1120 | eap | `mac` | `8232f00451d243499299f2b43d913f6669aeeb7ea2dcf47a3fca4a6c94e9af68` | Retrying | 0/5 | 2026-11-09T17:00:37.288778+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.922 | eap | `mac` | `bf3c3a3b99914ca7c0ff914abe6e3e9882c7b0f823cc29d4c756b3924eba1e26` | Retrying | 0/5 | 2026-11-09T17:00:29.283436+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.635 | eap | `mac` | `549d3dd05b4c7ac9e7d3c06ffd9ceb617667f3e664681555097d83959523d673` | Retrying | 0/5 | 2026-11-10T15:32:21.241516+00:00 | application: Invalid application metadata: Invalid file |
| 2020.1 | 201.515 | eap | `mac` | `c848320a5fdc7378a6f8405212956fd8183d62a0afe2076df1fe2c269e9c4925` | Retrying | 0/5 | 2026-11-10T15:32:52.423978+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.7 | 193.1623 | release | `mac` | `cc387ec32bc6cee302edb9d424158a781ebdaf7382d17fceaa56bb87906503e2` | Retrying | 0/5 | 2026-11-09T16:01:06.210077+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.6 | 193.1617 | release | `mac` | `3aa26b5e953bc205f78849dee9f597b905ee22a5d0bca4132da83ce4169f1b5d` | Retrying | 0/5 | 2026-11-09T16:01:24.342830+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.5 | 193.1569 | release | `mac` | `5dab45a650ced38469f67adbadc7e6eeaf4657306b7bc3acff0d7d90caf4c3e0` | Retrying | 0/5 | 2026-11-09T17:00:02.387522+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.4 | 193.1497 | release | `mac` | `2882fba44d34f292bd7dc5b431f99901b554e797fe181549bdcfeb15f154c263` | Retrying | 0/5 | 2026-11-09T17:00:23.278547+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.3 | 193.1331 | release | `mac` | `b271420b4e26f828d17e432ea84ed6762560c395cf202917369e6c44edbe069a` | Retrying | 0/5 | 2026-11-10T15:32:31.556101+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.2 | 193.1270 | release | `mac` | `96a4ab8cbc2d0327a1dcfcc5ccd40b38368ac379a7983cfd4645dc27842cdd8e` | Retrying | 0/5 | 2026-11-10T15:33:15.400999+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3.1 | 193.1223 | release | `mac` | `3c4674bb99b5fa95490de7c2b08bb6176690da7cf254bab85adb04bafe794f72` | Retrying | 0/5 | 2026-11-10T15:33:38.540228+00:00 | application: Invalid application metadata: Invalid file |
| 2019.3 | 193.1166 | release | `mac` | `a6aeaf37bf487626864c10ed82c54181004920808c342263fc93b57419b9474e` | Retrying | 0/5 | 2026-11-10T15:33:58.584773+00:00 | application: Invalid application metadata: Invalid file |
| 2019.2.4 | 192.2456 | release | `mac` | `4095ae7e98480ccf05b6474c6dba5fba736149c74c0aa8c53146b97587dda9af` | Retrying | 0/5 | 2026-11-10T15:34:20.036364+00:00 | application: Invalid application metadata: Invalid file |
| 2019.2.3 | 192.2321 | release | `mac` | `24e5adbd156455c695c26fabbe5dc9b9dfd2790b03a6bb8e9845cb67428b780f` | Retrying | 0/5 | 2026-11-10T15:34:44.303183+00:00 | application: Invalid application metadata: Invalid file |
| 2019.2.2 | 192.2288 | release | `mac` | `60a024e04e123233c9daa6ceb931d287d4f64c419fd902e968cd80a3e6a5ff50` | Retrying | 0/5 | 2026-11-10T15:35:09.136717+00:00 | application: Invalid application metadata: Invalid file |
| 2019.2.1 | 192.2176 | release | `mac` | `d42158b6b2524ba745e8f16616be6aaf3dbc5e55915cea5390a75cc2ee3d52ba` | Retrying | 1/5 | 2026-11-10T20:17:58.592708+00:00 | application: Invalid application metadata: Invalid file |
| 2019.2 | 192.2072 | release | `mac` | `dde50b6a558a0a25c2b157f555cf29f71401b0962218a437b827c259055c4ba8` | Retrying | 1/5 | 2026-11-10T20:18:19.543948+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.6 | 191.1698 | release | `mac` | `11fd6309a65a7b4b3773befbf4097bc7d39df101f939217ad5e3973d968046d0` | Retrying | 0/5 | 2026-11-10T15:34:30.403659+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.5 | 191.1593 | release | `mac` | `a838a769b7247725844232621efca81688ff431fca6e9482be8fa326c10476c1` | Retrying | 1/5 | 2026-11-10T20:18:33.808300+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.4 | 191.1577 | release | `mac` | `411f5ea3e6ce3b9b637184afe48167fe6fa974c7534d2d4a2d7f7083663da6f6` | Retrying | 1/5 | 2026-11-10T20:18:46.287260+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.3 | 191.1525 | release | `mac` | `9691bc011412c51a930d4944fac984c54861b88c70928c9a2109405d46bc8b4c` | Retrying | 1/5 | 2026-11-10T20:19:01.519131+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.2 | 191.1476 | release | `mac` | `2a5a0c946cd6feedc77916d4b75225a1fac0772808fbf38ec22582767c902a4e` | Retrying | 1/5 | 2026-11-10T20:19:30.378499+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1.1 | 191.1434 | release | `mac` | `742e31b6f992b752eaad5b5284ebb5f69f9bbaa272fb6154e13711cee5fa5f38` | Retrying | 1/5 | 2026-11-10T20:19:39.287941+00:00 | application: Invalid application metadata: Invalid file |
| 2019.1 | 191.1384 | release | `mac` | `c9ca83f3a05b20950883478df5610a48f9a1a33462e18d41f9cdf4b595ca2de2` | Retrying | 1/5 | 2026-11-10T20:19:52.453666+00:00 | application: Invalid application metadata: Invalid file |
| 2018.3.7 | 183.1868 | release | `mac` | `83bfa24d1df510699397ace9af9e211148178fe5d8e3aa0495bf3524fa533818` | Retrying | 1/5 | 2026-11-10T20:19:14.937502+00:00 | application: Invalid application metadata: Invalid file |
| 2018.2.6 | 182.1603 | release | `mac` | `f84cbaf0fc8b8c49d95a4bc5502cb4e88cc8f6f85da065f8d048424a96aebb73` | Retrying | 1/5 | 2026-11-10T20:20:00.360094+00:00 | application: Invalid application metadata: Invalid file |
| 2018.1.5 | 181.1469 | release | `mac` | `aa6c938cb9fa3eeefb1cd4a8f232e5819c995d5a53d5345bcb43eee916a83554` | Retrying | 0/5 | 2026-11-09T01:18:56.276664+00:00 | application: Invalid application metadata: Invalid file |
| 2017.3.6 | 173.1812 | release | `mac` | `b44eebc63bf9ad57654a6d8c2b799aab9f331baf973f94fcecb34a61364b11d7` | Retrying | 0/5 | 2026-11-09T01:19:12.342071+00:00 | application: Invalid application metadata: Invalid file |
| 2017.2.3 | 172.1493 | release | `mac` | `2640499fceeef83fce5bdbdf799a7ea1eb468f8fd4ca340263a7f8ba91956bd3` | Retrying | 0/5 | 2026-11-09T01:19:29.369901+00:00 | application: Invalid application metadata: Invalid file |
| 2017.1.3 | 171.1448 | release | `mac` | `70b1b63b7586cfd5fbddfcb440ab04a1af34bad919c9a4d127e34cf7c24a2c27` | Retrying | 0/5 | 2026-11-09T01:19:44.273412+00:00 | application: Invalid application metadata: Invalid file |
| 3.4.4 | 162.2317 | release | `mac` | `068cad86ae8fa40674e3b663328587b466a4c3a0560b0789746e77953260030e` | Retrying | 0/5 | 2026-11-09T01:19:59.352001+00:00 | application: Invalid application metadata: Invalid file |
| 3.3.5 | 143.1301 | release | `mac` | `ecde1c1faf4d425a69c44befaf19b64068e74a1ca2dd9044c4b750f996b8254a` | Retrying | 0/5 | 2026-11-09T01:20:24.469861+00:00 | application: Invalid application metadata: Invalid file |
| 3.2.4 | 139.2747 | release | `mac` | `21bb65a59759a6b266006f3dbac2fc8b51ee060bbd7d6213180ff8ed0a99a914` | Retrying | 0/5 | 2026-11-09T01:20:12.393158+00:00 | application: Invalid application metadata: Invalid file |

## PhpStorm (`PS`)

[Product table](PS.md) | [JSON history](../data/PS.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018.3.6 | 183.6156.29 | release | `mac` | `00764bd3f9fcb2694c3691292f4d323c3575e9057b33cd17cd36c532dc43a27c` | Retrying | 1/5 | 2026-11-10T20:23:57.917019+00:00 | application: Installer SHA-256 mismatch: expected 00764bd3f9fcb2694c3691292f4d323c3575e9057b33cd17cd36c532dc43a27c, got b2bfc36b835840f7cfec1071ad83da31dd6a199319425eb554808d2aa4ed02cc. The historical URL may have been replaced. |
| 3.0.3 | 111.271 | release | `mac` | `088da95aec3d05722da182cdf7379becfc4f01dc843e84181d4ca8d0a0e93581` | Retrying | 1/5 | 2026-11-10T20:23:56.397945+00:00 | application: Bundle build mismatch: API says 111.271, bundle says PS-111.344; refusing to attribute this executable to the wrong build |

## PyCharm (`PCP`)

[Product table](PCP.md) | [JSON history](../data/PCP.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.5.4 | 107.756 | release | `mac` | `1ce83ae7168f37a3d6fd02d76ecb2fb71a03957d66bd2c00dfa37f89537f29b1` | Retrying | 1/5 | 2026-11-10T20:22:27.633361+00:00 | application: Bundle build mismatch: API says 107.756, bundle says PY-107.576; refusing to attribute this executable to the wrong build |

## Youtrack Workflow Editor (`YTWE`)

[Product table](YTWE.md) | [JSON history](../data/YTWE.json)

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6.0 | 3385 | release | `mac` | `113749a54abd6c537bf1838a91cf35a70b2fdf04cfc4880eb906448b3156053e` | Retrying | 1/5 | 2026-11-10T20:30:37.658214+00:00 | application: Invalid application metadata: Invalid file |
