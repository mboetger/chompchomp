import React from 'react';
import Stack from 'react-bootstrap/Stack';
import ListGroup from 'react-bootstrap/ListGroup';

const Domain = ({ data }) => {
  const renderListItem = (label, value) => {
    if (Array.isArray(value)) {
      return (
        <ListGroup.Item key={label}>
          <strong>{label}:</strong>
          <ul>
            {value.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </ListGroup.Item>
      );
    } else {
      return (
        <ListGroup.Item key={label}>
          <strong>{label}:</strong> {value || 'N/A'}
        </ListGroup.Item>
      );
    }
  };

  return (
    <Stack gap={3}>
      <h1>Domain: <a href={data.domain}>{data.domain}</a></h1>
      <h6>Scanned On: {data.domain.date || "Unknown"}</h6>
      {data.whois ? (
        <ListGroup>
          {renderListItem('Domain Name', data.whois.domain_name)}
          {renderListItem('Registrar', data.whois.registrar)}
          {renderListItem('Registrar URL', <a href={data.whois.registrar_url}>{data.whois.registrar_url}</a>)}
          {renderListItem('Whois Server', data.whois.whois_server)}
          {renderListItem('Updated Date', data.whois.updated_date)}
          {renderListItem('Creation Date', data.whois.creation_date)}
          {renderListItem('Expiration Date', data.whois.expiration_date)}
          {renderListItem('Status', data.whois.status)}
          {renderListItem('Emails', data.whois.emails)}
          {renderListItem('DNSSEC', data.whois.dnssec)}
          {renderListItem('Name', data.whois.name)}
          {renderListItem('Organization', data.whois.org)}
          {renderListItem('Address', data.whois.address)}
          {renderListItem('City', data.whois.city)}
          {renderListItem('State', data.whois.state)}
          {renderListItem('Postal Code', data.whois.registrant_postal_code)}
          {renderListItem('Country', data.whois.country)}
          {renderListItem('Name Servers', data.whois.name_servers)}
        </ListGroup>
      ) : null}
    </Stack>
  );
};

export default Domain;