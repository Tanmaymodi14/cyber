import boto3

def collect(session: boto3.Session) -> dict:
    cf = session.client('cloudfront')
    distributions = []
    marker = None
    try:
        while True:
            if marker:
                resp = cf.list_distributions(Marker=marker)
            else:
                resp = cf.list_distributions()
            items = (resp.get('DistributionList', {}) or {}).get('Items', [])
            for d in items:
                dist = {
                    'Id': d.get('Id'),
                    'DomainName': d.get('DomainName'),
                    'Enabled': d.get('Enabled'),
                    'ViewerProtocolPolicy': None,
                    'MinTLSVersion': None
                }
                # Attempt to infer TLS policy from default cache behavior
                try:
                    conf = cf.get_distribution_config(Id=d.get('Id'))
                    default_cache = conf.get('DistributionConfig', {}).get('DefaultCacheBehavior', {})
                    dist['ViewerProtocolPolicy'] = default_cache.get('ViewerProtocolPolicy')
                    
                    # Extract MinTLSVersion from ViewerCertificate
                    viewer_cert = conf.get('DistributionConfig', {}).get('ViewerCertificate', {})
                    dist['MinTLSVersion'] = viewer_cert.get('MinimumProtocolVersion')
                    
                    # Extract session settings for AC-10/11/12 controls
                    dist['SessionTimeout'] = default_cache.get('DefaultTTL') or 3600
                    dist['IdleTimeout'] = default_cache.get('MinTTL') or 0
                    
                    # Extract WAF association for AC-4
                    dist['WebACLId'] = conf.get('DistributionConfig', {}).get('WebACLId')
                except Exception:
                    pass
                distributions.append(dist)
            if not (resp.get('DistributionList', {}) or {}).get('IsTruncated'):
                break
            marker = (resp.get('DistributionList', {}) or {}).get('NextMarker')
    except Exception:
        pass
    return {'cloudfront': {'distributions': distributions}}
